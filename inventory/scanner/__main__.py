#!/usr/bin/env python3
#
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

from inventory.scanner.streamers import GStreamer, OpenCVStreamer
from inventory.scanner.dataprocessing import ProcessCount
from inventory.scanner.coordination import Coordinator
from inventory.scanner.runners import Parameters
from inventory.scanner import version
from inventory.scanner import logger
import argparse
import os


def simulate(process_count: ProcessCount):
    """
    """
    from inventory.scanner.dataprocessing import ShelfImage
    from PIL import Image
    import numpy as np
    import glob
    import os

    images = glob.glob(os.path.join("C:/Users/johns/Documents/EngineeringCapstone/inventory-scanner/test/stitching/synthetic_4","*.jpg"))

    shelf_panorama = Image.open("C:/Users/johns/Documents/EngineeringCapstone/inventory-scanner/test/stitching/synthetic_6/show_all.jpg")
    shelf_panorama = np.asarray(shelf_panorama)

    # if len(images) == 0:
    #     raise RuntimeError("No images found")
    # # images = [
    # #     "C:/Users/johns/Documents/EngineeringCapstone/inventory-scanner/test/stitching/synthetic/shelf_1.jpg",
    # #     "C:/Users/johns/Documents/EngineeringCapstone/inventory-scanner/test/stitching/synthetic/shelf_2.jpg",
    # # ]
    # shelf_image = ShelfImage()

    # for image in images:
    #     image = np.ascontiguousarray(Image.open(image).convert('RGB'))
    #     shelf_image._shelf_segments.append(image)

    process_count.process(shelf_panorama)
    

def start_application(args):
    """
    This function starts the inventory scanner application.

    Parameters
    ----------
        args: argsparse.NameSpace
            These are the command line arguments that was set.
    """
    parameters = Parameters(
        detection_score=args.detection_score,
        detection_iou=args.detection_iou,
        acceptance_score=args.acceptance_score,
        max_detections=args.max_detections,
        normalization=args.normalization,
        warmup=args.warmup
    )

    if isinstance(args.results_out, str):
        if not os.path.exists(args.results_out):
            logger(f"{args.results_out} does not exist, creating the directories.", 
                   code="INFO")
            os.makedirs(args.results_out)

    count_processor = ProcessCount(
        path_package_model=args.package_model,
        path_identification_model=args.identification_model,
        parameters=parameters,
        show=args.show,
        results_out=args.results_out
    )
    # simulate(count_processor)

    # exit(1)
    coordinator = Coordinator(
        path_shelf_model=args.shelf_model,
        parameters=parameters,
        show=args.show
    )
    
    if args.application.lower() == "gstreamer":
        streamer = GStreamer(
            source=args.camera,
            count_processor=count_processor,
            coordinator=coordinator
        )
        streamer.run()
    elif args.application.lower() == "opencv":
        source = args.camera
        if source.isdecimal():
            source = int(source)
            streamer = OpenCVStreamer(
                source=source,
                count_processor=count_processor,
                coordinator=coordinator,
                fps=args.fps,
                resolution=args.resolution,
                show=args.show
            )
            streamer.run()
        else:
            raise TypeError(
                "OpenCV streaming accepts an integer index for the camera source. " +
                f"Recieved {source}")
    else:
        raise ProcessLookupError(
            f"The application: {args.application} is currently not supported.")

def main():
    """
    Define the command line arguments to start the application.
    """
    parser = argparse.ArgumentParser(
        description=("Standalone Inventory Scanner"),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-v', '--version', 
                        help="Print the project version.",
                        action='version',
                        version=version())
    parser.add_argument("--verbose", 
                        help=("This allows logging messages to the terminal."),
                        action="store_true")
    parser.add_argument("--application",
                        help=("Specify the type of application to "
                              "process frames."),
                        type=str,
                        choices=["gstreamer", "opencv"],
                        default="gstreamer")
    parser.add_argument("-c", "--camera", 
                        help=("Specify the camera source to use for streaming."
                              "GStreamer option accepts the format /dev/video0,"
                              "... OpenCV options takes an integer such as 0."),
                        type=str,
                        default="/dev/video0")
    parser.add_argument("-f", "--fps",
                        help=("Set the stream frames per second."),
                        type=int,
                        default=30)
    parser.add_argument("-r", "--resolution",
                        help=("Set the resolution of the frame (width, height)."),
                        type=tuple,
                        default=(1920, 1080))
    parser.add_argument("--show",
                        help=("Show the frame with the overlaid bounding boxes."),
                        action="store_true")
    parser.add_argument("--results_out",
                        help=("Path to store the CSV and image bounding box overlays."),
                        type=str)
    parser.add_argument("--sharpen",
                        help=("Provide the number of times to sharpen the image. "
                              "This is used to enhance detected barcode/QR code images."),
                        type=int,
                        default=0)
    parser.add_argument("--detection_score",
                        help=("The score threshold to set for the NMS."),
                        type=float,
                        default=0.001)
    parser.add_argument("--detection_iou",
                        help=("The IoU threshold to set for the NMS."),
                        type=float,
                        default=0.60)
    parser.add_argument("--acceptance_score",
                        help=("The score threshold to consider as valid detections."),
                        type=float,
                        default=0.10)
    parser.add_argument("--normalization",
                        help=("The type of image normalization to perform."),
                        choices=["signed", "unsigned", "raw"],
                        type=str,
                        default="unsigned")
    parser.add_argument("--max_detections",
                        help=("The maximum detections to set for the NMS."),
                        type=int,
                        default=300)
    parser.add_argument("--warmup",
                        help=("The number of model warmup iterations to perform "
                              "prior for inference."),
                        type=int,
                        default=0)
    parser.add_argument("-p", "--package_model",
                        help=("The path to the KerasRetinanet package model."),
                        type=str,
                        required=True)
    parser.add_argument("-i", "--identification_model",
                        help=("The path to the TFLite barcode/QRCode model."),
                        type=str,
                        required=True)
    parser.add_argument("-s", "--shelf_model",
                        help=("The path to the TFLite shelf detection model."),
                        type=str,
                        required=True)
    args = parser.parse_args()

    start_application(args)

if __name__ == "__main__":
    main()