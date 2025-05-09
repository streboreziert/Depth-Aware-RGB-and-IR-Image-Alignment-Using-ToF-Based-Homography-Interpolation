import imageio.v2 as imageio
import numpy as np

image_16bit = imageio.imread("ir.tif")

image_min = np.min(image_16bit)
image_range = np.ptp(image_16bit)  # <- updated!
image_8bit = ((image_16bit - image_min) / image_range * 255).astype(np.uint8)

imageio.imwrite("ir_8bit.tif", image_8bit)

print("converted")