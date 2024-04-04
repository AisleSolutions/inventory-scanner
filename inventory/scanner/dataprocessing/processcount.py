# Copyright 2024 by AisleSolutions. All Rights Reserved. 
# 
# Source code is explicitly for meeting requirements requested by University
# of Calgary Entrepreneurial Capstone Design Project 2024. 
#
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying source code is explicitly forbidden. 

from __future__ import annotations
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from inventory.scanner.dataprocessing import ShelfImage
    from inventory.scanner.runners import Parameters

from inventory.scanner.dataprocessing.utils import (
    draw_bounding_box,
    draw_text
)
from inventory.scanner.dataprocessing.matchdetections import MatchDetections
from inventory.scanner.dataprocessing.categorizetext import CategorizeText
from inventory.scanner.dataprocessing.inventoryimage import PackageImage
from inventory.scanner.dataprocessing.processthread import DataThread
from inventory.scanner import logger
from PIL import Image, ImageDraw
import numpy as np
import os


class ProcessCount:
    """
    This class performs multithreading to provide separate threads for 
    detecting packages, barcodes/QRcodes, etc.

    The detections are then processed to infer on the package counts and
    the barcodes/QRCodes they belong to for classification. 

    Single threads should be provided for the following:
    1) Package detections -> Each detection is cropped and any text is searched.
    2) Barcode/QR code detections.
    
    Then once the threads are merged, the packages and detected barcodes/QR codes
    are paired. Only one barcode/QR code should be paired per detection.

    The package detections that did not have a barcode/QR code or texts 
    will not be considered as valid packages. The result should yeild the 
    following tuple:: \
        (
            cropped package image: InventoryImage, 
            text: str,
            barcode/QR code: InventoryImage
        )

    Parameters
    -----------
        path_package_model: str
            This is the path to the package detection model.

        path_identification model: str
            This is the path to the model that detects barcodes and QR codes.

        parameters: Parameters
            This contains the model parameters to control the model's
            behaviour.

        show: bool
            Specify whether to show the image with overlain bounding boxes
            of the detections.

        results_out: str
            The path to save the csv results of the counts and the image of 
            the shelf with visualizations.
    """
    def __init__(
            self,
            path_package_model: str,
            path_identification_model: str,
            parameters: Parameters,
            show: bool=False,
            results_out: str=None,
        ) -> None:
        
        from inventory.scanner.runners import (
            IdentificationDetector, 
            PackageDetector, 
            TextDetector
        )
        self.package_detector = PackageDetector(
            model=path_package_model,
            parameters=parameters
        )
        self.identification_detector = IdentificationDetector(
            model=path_identification_model,
            parameters=parameters
        )
        self.text_detector = TextDetector()
        self.show = show
        self.results_out = results_out
        self.shelf_id = 0

    def process(
            self, 
            shelf_image: Union[ShelfImage, np.ndarray],
            detect_code: bool=False,
        ):
        """
        Stitch images -> process packages 
                      -> process codes/process texts
                      -> retrieve package counts

        Parameters
        ----------
            shelf_image: ShelfImage, np.ndarray
                The object that contains the image segments of the shelving
                to stitch and process for counts.
                If a numpy array is passed, then do not stitch the image, but
                process it only.

            detect_code: bool
                If this is true, identify packages by their QRCodes or Barcodes.
                Otherwise identify them by their texts.
        """

        if isinstance(shelf_image, np.ndarray):
            shelf_panorama = shelf_image
        else:
            shelf_panorama = shelf_image.stitch_images()
            if shelf_panorama is None:
                logger("Stitched image returned None.", code="WARNING")
                return

        """Thread 1 Detect packages"""
        package_thread = DataThread(
            target=self.package_detector.detect, args=(shelf_panorama,))
    
        if detect_code:
            """Thread 2 Detect barcodes/QR codes"""
            identification_thread = DataThread(
                target=self.identification_detector.detect, args=(shelf_panorama,))
            identification_thread.start()
        else:
            """Thread 3 Detect Texts"""
            text_thread = DataThread(
                target=self.text_detector.detect, args=(shelf_panorama,))
            text_thread.start()
        package_thread.start()
        
        """Join Threads"""
        if detect_code:
            # returns boxes, scores, labels (0: barcode, 1: qrcode).
            code_boxes, _, _ = identification_thread.join()
        else:
            # returnes boxes, scores, texts
            text_boxes, _, texts = text_thread.join()
        # returns boxes, scores, labels (labels are always 0 unfortunately).
        package_boxes, _, _ = package_thread.join()
        
        """Initialize Matchers"""     
        if detect_code:   
            """Thread 4 Match packages to barcodes/QR codes + decode"""
            match_package_code = MatchDetections(
                ground_truths=package_boxes,
                predictions=code_boxes,
                group=True
            )
            match_code_thread = DataThread(
                target=match_package_code.match, args=())
            match_code_thread.start()

            # TODO: Decode code and classify

            """Join Threads"""

            """
            Create PackageImage based on decoded barcode/QR code. Collect
            packages with the same decoded information.
            """

        else:
            """Thread 5 Match packages to texts"""
            if len(package_boxes) > 0 and len(text_boxes) > 0:
                match_package_text = MatchDetections(
                    ground_truths=package_boxes,
                    predictions=text_boxes,
                )
                match_text_thread = DataThread(
                    target=match_package_text.match, args=())
                
                text_classifier = CategorizeText(texts, text_boxes)
                text_classifier_thread = DataThread(
                    target=text_classifier.categorize_by_common_text, args=()
                )
                
                match_text_thread.start()
                text_classifier_thread.start()

                """Join Threads"""
                match_text_thread.join()
                text_classifier_thread.join()

                """
                Categorize text detected, create PackageImage based on the text 
                category. Collect packages with the same text category.
                """
                collected_packages = self.process_text_counts(
                    match_package_text, text_classifier)

                if self.results_out is not None:
                    self.save_csv(collected_packages)
                    shelf_panorama = self.visualize(
                        shelf_panorama, package_boxes, text_boxes, texts)

                if self.show and self.results_out is None:
                    self.save_csv(collected_packages, save=False)
                    shelf_panorama = self.visualize(
                        shelf_panorama, 
                        package_boxes, 
                        text_boxes, 
                        texts, 
                        save=False)

        self.shelf_id += 1
        return shelf_panorama

    def process_text_counts(
            self, 
            match_package_text: MatchDetections,
            text_classifier: CategorizeText, 
        ) -> list:
        """
        Analyzes the matches and the text classifications into PackageImage 
        objects storing both the counts and the category for which the
        package belongs.

        Parameters
        ----------
            match_package_text: MatchDetections
                Contains the indices (package index, text index) that matches
                the package bounding boxes to the texts.

            text_classifier: CategorizeText
                Categorizes the text in terms of uniqueness.

        Returns
        --------
            collected_packages: list
                This contains the PackageImage objects that were created. 
        """
        collected_packages = list()
        captured_keys = list()
        for match in match_package_text.index_matches:
            for key, value in text_classifier.categories.items():
                # Indicates the index of the matched text is inside the key category.
                if match[0] in value:
                    if key not in captured_keys:
                        package = PackageImage(key)
                        collected_packages.append(package)
                        captured_keys.append(key)
                    else:
                        package_index = captured_keys.index(key)
                        package = collected_packages[package_index]

                    package._count += 1
                    # Store the package bounding box.
                    package._boxes.append(match_package_text.ground_truths[match[1]])
                    break
        return collected_packages      

    def process_code_counts(self, image: np.ndarray):
        """
        Thread 2: Detect Barcodes and QR Codes -> Crop image -> Decode detections.

        Parameters
        ----------
            image: np.ndarray
                This is the image to detect barcodes and QR codes. This image
                should be the cropped package image.

        Returns
        -------

        """
        boxes, scores, labels = self.identification_detector.detect(image)
        if self.show:
            image_drawn = Image.fromarray(image)
            image_draw = ImageDraw.Draw(image_drawn)

        for box, score, label in zip(boxes, scores, labels):
            if self.show:
                draw_bounding_box(
                    image_draw, ((box[0], box[1]), (box[2], box[3])))

            # Decode the barcodes and QR codes by passing a cropped image to 
            # the zxing-cpp dependency.
            image_copy = image.copy()
            image_cropped = image_copy[box[1]:box[3], box[0]:box[2], :]

            decodes = self.identification_detector.decode(image_cropped)

            # Assuming only one barcode/QR code was decoded because it is
            # passing an image containing only one code.
            decode = None
            if len(decodes) > 0:
                decode = decodes[0]

            if self.show:
                if label == 0:
                    text = f"Barcode {round(score*100, 2)}"
                elif label == 1:
                    text = f"QR Code {round(score*100, 2)}"
                else:
                    text = f"{label} {round(score*100, 2)}"

                if decode is not None:
                    text += f"{decode.text}, {decode.format}, {decode.content_type}"

    def visualize(
        self,
        image: np.ndarray, 
        package_boxes: np.ndarray, 
        label_boxes: np.ndarray, 
        labels: list,
        save: bool=True
    ) -> np.ndarray:
        """
        Visualizes the detected packages and the texts into an image with
        bounding box and text overlays describing the scenario. Saves the image
        visualization as a PNG file depending on the visualize out parameter set.

        Parameters
        ----------
            image: np.ndarray
                The image to overlay and visualize.

            package_boxes: np.ndarray
                The detected package bounding boxes.

            label_boxes: np.ndarray
                The detected text or barcode/qrcode bounding boxes.

            labels: list
                This contains the detected texts or decoded information.

            save: bool
                Specify whether to save the image as a numpy file.

        Returns
        -------
            image: np.ndarray
                The image with drawn bounding boxes.
        """
        height, width, _ = image.shape

        # Convert normalized bounding boxes back to pixel values.
        package_boxes[..., 0] = package_boxes[..., 0] * width
        package_boxes[..., 1] = package_boxes[..., 1] * height
        package_boxes[..., 2] = package_boxes[..., 2] * width
        package_boxes[..., 3] = package_boxes[..., 3] * height

        label_boxes[..., 0] = label_boxes[..., 0] * width
        label_boxes[..., 1] = label_boxes[..., 1] * height
        label_boxes[..., 2] = label_boxes[..., 2] * width
        label_boxes[..., 3] = label_boxes[..., 3] * height

        image_drawn = Image.fromarray(image)
        image_draw = ImageDraw.Draw(image_drawn)

        for box in package_boxes:
            box = box.astype(int)
            draw_bounding_box(
                image_draw, 
                ((box[0], box[1]), (box[2], box[3])), 
                color="RoyalBlue")
        
        for box, label in zip(label_boxes, labels):
            box = box.astype(int)
            draw_bounding_box(
                image_draw, ((box[0], box[1]), (box[2], box[3])))
            draw_text(image_draw, label, (box[0], box[1]-10), color="black")
       
        if save:
            image_drawn.save(os.path.join(self.results_out, 
                                        f"shelf_{self.shelf_id}.png"))
        return np.asarray(image_drawn)

    def save_csv(self, collected_packages: list, save: bool=True):
        """
        Saves the package count results as a CSV.

        Parameters
        -----------
            collected_packages: list
                This contains PackageImage objects storing the counts and the
                package labels.

            save: bool
                Specify whether to save the image as a numpy file.
        """
        labels, counts = list(), list()
        for package in collected_packages:
            package: PackageImage
            print(f"{package._label}: {package._count}")
            labels.append(package._label)
            counts.append(package._count)
        print("\n")

        if save:
            np.savetxt(os.path.join(self.results_out, f"shelf_{self.shelf_id}.csv"), 
                    [p for p in zip(labels, counts)], 
                    delimiter=',', 
                    fmt='%s')
