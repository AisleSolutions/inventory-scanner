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

from PIL import Image
import numpy as np
import zxingcpp
import os


def test_barcode_qrcode_decoder():
    """
    Test if the dependency is detecting barcodes and QR codes properly.
    """
    # QR Code example
    image = np.ascontiguousarray(Image.open(
        os.path.join(os.path.dirname( __file__ ), 
                     "samples/qrcode_001.jpg")).convert('RGB'))
    qrcodes = zxingcpp.read_barcodes(image)
    assert len(qrcodes) > 0

    for qrcode in qrcodes:
        assert qrcode.text == "https://www.ao-covidtracer.corplite.com/qr/PZp11Ji39"
        assert str(qrcode.format) == "BarcodeFormat.QRCode"
        assert str(qrcode.content_type) == "ContentType.Text" #NOSONAR
        
    # Barcode examples
    image = np.ascontiguousarray(Image.open(
        os.path.join(os.path.dirname( __file__ ), 
                     "samples/barcode_001.jpg")).convert('RGB'))
    barcodes = zxingcpp.read_barcodes(image)
    assert len(barcodes) > 0

    for barcode in barcodes:
        assert barcode.text == "12014895885"
        assert str(barcode.format) == "BarcodeFormat.Code128"
        assert str(barcode.content_type) == "ContentType.Text"

    image = np.ascontiguousarray(Image.open(
        os.path.join(os.path.dirname( __file__ ), 
                     "samples/barcode_004.png")).convert('RGB'))
    barcodes = zxingcpp.read_barcodes(image)
    assert len(barcodes) > 0

    for barcode in barcodes:
        assert barcode.text == "705632441947"
        assert str(barcode.format) == "BarcodeFormat.UPCA"
        assert str(barcode.content_type) == "ContentType.Text"

def test_text_detector():
    """
    Test if the dependency is detecting text properly.
    """
    from inventory.scanner.runners import TextDetector
    text_detector = TextDetector()

    image = np.ascontiguousarray(Image.open(
        os.path.join(os.path.dirname( __file__ ), 
                     "samples/coffee_package_001.png")).convert('RGB'))
    _, _, texts = text_detector.detect(image)
    
    expected = ['phil', 'sebastian', 'coffee', 'rosters', 'the', 'doppelganger', 'silk', 'comfortable', 'chocolate', 'ocfrebeans']
    for text in texts:
        assert text in expected
    
    image = np.ascontiguousarray(Image.open(
        os.path.join(os.path.dirname( __file__ ), 
                     "samples/coffee_package_002.png")).convert('RGB'))
    _, _, texts = text_detector.detect(image)
    
    expected = ['phil', 'sebastian', 'coffee', 'rosters', 'little', 'sky', 'honduras', 'ncs', 'att', 'approachable', 'nuanced', 'us']
    for text in texts:
        assert text in expected
    

"""
To run:
python -m pytest
"""
