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
from inventory.scanner.runners import Parameters
from inventory.scanner import version
import argparse

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
    count_processor = ProcessCount(
        path_package_model=args.package_model,
        path_identification_model=args.identification_model,
        parameters=parameters
    )
    
    if args.application.lower() == "gstreamer":
        streamer = GStreamer(
            source=args.camera,
            count_processor=count_processor
        )
        streamer.run()
    elif args.application.lower() == "opencv":
        source = args.camera
        if source.isdecimal():
            source = int(source)
            streamer = OpenCVStreamer(
                source=source,
                count_processor=count_processor,
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
    parser.add_argument("-s", "--show",
                        help=("Show the frame with the overlaid bounding boxes."),
                        action="store_true")
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
                        default=0.25)
    parser.add_argument("--normalization",
                        help=("The type of image normalization to perform."),
                        choices=["signed", "unsigned", "raw"],
                        type=str,
                        default="unsigned")
    parser.add_argument("--warmup",
                        help=("The number of model warmup iterations to perform "
                              "prior for inference."),
                        type=int,
                        default=0)
    parser.add_argument("-p", "--package_model",
                        help=("Specify the path to the package model."),
                        type=str,
                        required=True)
    parser.add_argument("-i", "--identification_model",
                        help=("Specify the path to the barcode/QRCode model."),
                        type=str,
                        required=True)
    args = parser.parse_args()

    start_application(args)

if __name__ == "__main__":
    main()