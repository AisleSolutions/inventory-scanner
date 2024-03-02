


import zxingcpp
from PIL import Image
import numpy as np

image = np.ascontiguousarray(Image.open('C:/Users/johns/Documents/EngineeringCapstone/inventory-extra/test/samples/qrcode_001.jpg').convert('RGB'))
barcodes = zxingcpp.read_barcodes(image)
print(f"{type(barcodes)=}")
for barcode in barcodes:
	print(f"{type(barcode.format)=}")
	print('Found barcode:'
		f'\n Text:    "{barcode.text}"'
		f'\n Format:   {barcode.format}'
		f'\n Content:  {barcode.content_type}'
		f'\n Position: {barcode.position}')
if len(barcodes) == 0:
	print("Could not find any barcode.")