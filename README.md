# Inventory-Scanner
This package provides functionalities for detecting and counting warehouse 
packages and to classify each package by detecting existing facing barcodes 
or QR codes on the packages.
*Note OpenCV or GStreamer is needed to run the application, please see the section [Supported Environments and Applications](#supported-environments-and-applications)* for more information for their installations as this could vary from system to system.

# Overview
- [Problem/Use Case](#problemuse-case)
- [Device Inventory Calibration Process](#device-inventory-calibration-process)
- [Device Inventory Counting Process](#device-inventory-counting-process)
- [Changelog](#changelog)
- [Installation](#installation)
    - [Manual Installation](#manual-installation)
    - [PIP Installation](#pip-installation)
- [Supported Environments and Applications](#supported-environments-and-applications)
    - [Python Supported Versions](#python)
    - [OpenCV Streaming Option](#opencv)
    - [GStreamer Streaming Option](#gstreamer)
- [Sample Commands](#sample-commands)
    - [Help Option](#help)
    - [OpenCV Streaming](#opencv-streaming-option)
    - [GStreamer Streaming](#gstreamer-streaming-option)
- [References](#references)

# Problem/Use Case
To efficiently and reliably track inventory changes in warehouses saving clients time and money from manual inventory tracking labour and possible errors. Package counts are generated classifying each package by the detected barcodes/QR codes or by the text that the algorithms detected on each package. Otherwise, images of the shelving are recorded for clients to visually inspect the count without the need for onsite inspection. 

# Device-Inventory Calibration Process
These steps are provided to allow the camera to be correctly oriented facing the shelving.

**Move towards the shelving**

![Shelving Detection Step 1 and 2](/doc/images/shelving_process_step_1.jpg)

1) Use the streamers and continuously detect shelving in the environment.

    * Determine angular direction of the shelving from the camera.

2) Move the device towards the shelving.

    * Orient the device to position in front of the shelving.

**Device Positioning and Calibration**

![Shelving Detection Step 3](/doc/images/shelving_process_step_3.jpg)

3) Apply the known variables to position the device such that the edge of the shelf is inside the viewing angle of the camera.

    * Camera viewing angle: Known

    * 2DLidar distance of device from shelf: Known

**Inventory Scanner Gather Package Counts**

4) Take the frame that contains the shelf and process the frame to get the inventory count. Details regarding this process is described in the next section.

5) Update the database.

    * Package: Barcode/QR Code, Texts, Count

    * Shelf Image (For manual verification).

**Multiple Shelving Dimensions**

![Shelving Detection Step 6](/doc/images/shelving_process_step_6.jpg)

6) Recalibrate the camera (apply rotations and elevations) to capture frames of the shelf that was not included.

7) Repeat steps 4 and 5.

**Traversing the Length of the Shelf**

![Shelving Detection Step 8](/doc/images/shelving_process_step_8.jpg)

8) Move the device in the x-direction to capture the rest of the sections of the shelf.

9) Repeat steps 4-7

# Device Inventory Counting Process

![Counting Process](/doc/images/counting_process.jpg)

# Changelog
*Date Release*: inventory-scanner 0.0.0: First Release

# Installation
Ensure to upgrade python's PIP with the following command.

```shell
python -m pip install --upgrade pip
```

When using linux it is best to update the upgrade the dependencies.

```shell
sudo apt update
```

```shell
sudo apt upgrade
```

It is best to start a new python virtual environment to keep all installed dependencies 
constained within the environment.

```shell
python -m venv "path to save the environment"
```

**Windows activate the environment**
```shell
"path to the environment"/Scripts/activate
```

**Linux activate the environment**
```shell
source "path to the environment"/bin/activate
```

*Note: Installation steps under [References](#references) are also relevant.*

## Manual Installation
*Coming soon...*

Install the package requirements
```shell
pip install -r requirements.txt
```

## PIP Installation
*Coming soon..*

# Supported Environments and Applications
Supported streaming dependencies are OpenCV and GStreamer. 
The package was verified to work on the following environments and applications.

## Python
Python 3.11.5 and 3.11.6

## OpenCV
OpenCV is an option for using a camera to capture the frames. This dependency
can be installed with the following command.

```shell
pip install opencv-python~=4.9.0
```

The environments tested to run this package using OpenCV:
* Raspberry PI 5: Ubuntu 23.10 (GNU/Linux 6.5.0-1011-raspi aarch64)
* Windows 10

## GStreamer
GStreamer is another option for using a camera to capture frames. This
dependency can be installed with the following command.

Install PyCairo
```shell
sudo apt install libcairo2-dev pkg-config python3-dev
```

Install GStreamer Dependencies
```shell
sudo apt install libgirepository1.0-dev
```

```shell
sudo apt install python3-gst-1.0
```

```shell
pip3 install PyGObject~=3.46.0
```

GStreamer installation faced difficulties when using Windows. So this package
supports the following environments:
* Raspberry PI 5: Ubuntu 23.10 (GNU/Linux 6.5.0-1011-raspi aarch64)

# Sample Commands

## Help
```shell
python -m inventory.scanner -h
```

## OpenCV Streaming Option
```shell
python -m inventory.scanner 
    --camera=0 
    --application=opencv 
    --show
    --package_model=inference-iou_resnet50_csv_06.h5 
    --identification_model=packages-best-99-fp16.tflite
    --shelf_model=shelves-best-fp16-epoch-99.tflite
```

## GStreamer Streaming Option

```shell
python3 -m inventory.scanner 
    --package_model=inference-iou_resnet50_csv_06.h5  
    --identification_model=barcode-best-fp16.tflite
    --shelf_model=shelves-best-fp16-epoch-99.tflite
```

## GStreamer Stream Functionality Check
If the application fails with GStreamer, this command runs the pipeline manually that
provides error message to be printed.

```shell
gst-launch-1.0 v4l2src device=/dev/video0 ! queue ! decodebin ! videoconvert ! video/x-raw, format=RGB ! appsink sync=true max-buffers=1 drop=true name=sink emit-signals=true
```

*Note: common errors found was due to `sudo` being required to run the application*

This command provides sudo access to the machine.

```shell
sudo -s
```

# References
[1] Running the package detection model uses the implementation from [keras-retinanet.](https://github.com/fizyr/keras-retinanet). The repository was cloned and the installation process was followed. However, an addition was made to the repository to include TFLite functionality. 
The installation process shown in the repository created the following files which is required to run the package model.

* Linux compiled: compute_overlap.cpython-311-aarch64-linux-gnu.so
* Windows compiled: compute_overlap.cp311-win_amd64.pyd

[2] The pretrained model for detecting packages was found in [SKU110K_CVPR19 repository](https://github.com/eg4000/SKU110K_CVPR19). The model was then converted as an inference model following instructions provided in the keras-retinanet repository. 

[3] The model for detecting barcodes and QR codes was trained using [YoloV5](https://github.com/ultralytics/yolov5). The dataset used to train the model was found in RoboFlow named as [barcodes-zmxjq_dataset](https://universe.roboflow.com/labeler-projects/barcodes-zmxjq). It is true that the dependency `zxing-cpp` is used to decode the barcodes and QR codes also provides positions of the detected codes. However, a size limit of the codes was observed to allow proper detections using this dependency alone. Smaller codes or samples that are far from the camera was detected using a trained model given that the dataset used to train this model had samples to overcome this difficulty. A decision was made to crop the detections from the trained model and pass those cropped images to the `zxing-cpp` dependency to decode the samples. 

[4] The model for detecting shelves was trained using [YoloV5](https://github.com/ultralytics/yolov5). The dataset used to train the model was found in RoboFlow named as [shelves Dataset](https://universe.roboflow.com/shelfdetect-yzkro/shelves-ugxt3). This model was trained for 99 epochs and then converted into a TFLite model using `export.py` in YoloV5.

[5] Deepview-validator Matching and TFLite