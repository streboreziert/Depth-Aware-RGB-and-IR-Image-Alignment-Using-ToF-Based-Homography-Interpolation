import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Load RGB and IR images
rgb_img = np.array(Image.open("rgb.tif").convert("RGB"))
ir_img = np.array(Image.open("ir.tif").convert("RGB"))

# Convert RGB to grayscale and stack to 3 channels
rgb_gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
rgb_gray_stack = np.stack([rgb_gray] * 3, axis=-1)

# Convert IR to grayscale
gray_ir = cv2.cvtColor(ir_img, cv2.COLOR_RGB2GRAY)

# Threshold and quantize IR
threshold = 50
levels = 6
step = 256 // levels
gray_ir_masked = np.where(gray_ir > threshold, gray_ir, 0).astype(np.uint8)
quantized = ((gray_ir_masked // step) * step).astype(np.uint8)

# Apply Inferno colormap
normed = quantized.astype(np.float32) / 255.0
colored_ir = (cm.inferno(normed)[..., :3] * 255).astype(np.uint8)
colored_ir[quantized == 0] = 0
ir_heatmap = colored_ir

# Load depth data
depth = np.loadtxt("interpolated_z.txt", skiprows=1)

# Image dimensions
ir_w, ir_h = 320, 240
rgb_w, rgb_h = 1024, 760

# Homography coefficients
ir_coeffs = {
    'H11': (1.09040, -0.000234), 'H12': (-0.17168, 0.000011), 'H13': (165.02078, 0.00764),
    'H21': (0.04629, -0.000133), 'H22': (0.89844, -0.000019), 'H23': (74.10048, -0.00217),
    'H31': (0.000176, -0.00000061), 'H32': (-0.000598, 0.000000099), 'H33': (1.0, -2.18e-12)
}
rgb_coeffs = {
    'H11': (0.29816, 0.0000289), 'H12': (-0.04691, -0.0000075), 'H13': (175.13348, -0.00616),
    'H21': (-0.01343, 0.0000220), 'H22': (0.28601, 0.0000095), 'H23': (116.28422, -0.01694),
    'H31': (-0.000068, 0.000000068), 'H32': (-0.000142, -0.000000019), 'H33': (1.0, -2.18e-12)
}

# Function to get homography
def get_H(coeffs, d_cm):
    return np.array([
        [coeffs['H11'][0] + coeffs['H11'][1]*d_cm, coeffs['H12'][0] + coeffs['H12'][1]*d_cm, coeffs['H13'][0] + coeffs['H13'][1]*d_cm],
        [coeffs['H21'][0] + coeffs['H21'][1]*d_cm, coeffs['H22'][0] + coeffs['H22'][1]*d_cm, coeffs['H23'][0] + coeffs['H23'][1]*d_cm],
        [coeffs['H31'][0] + coeffs['H31'][1]*d_cm, coeffs['H32'][0] + coeffs['H32'][1]*d_cm, coeffs['H33'][0]]
    ])

# Warp IR heatmap using depth + homography
warped_ir = np.zeros_like(rgb_img)
mask = np.zeros(rgb_img.shape[:2], dtype=bool)

for row, col, z in depth:
    pt = np.array([col, row, 1])
    d_cm = -z / 10.0 if z != 0 else 0

    ir_pt = np.linalg.inv(get_H(ir_coeffs, d_cm)) @ pt
    rgb_pt = np.linalg.inv(get_H(rgb_coeffs, d_cm)) @ pt
    ir_pt /= ir_pt[2]
    rgb_pt /= rgb_pt[2]

    ir_x, ir_y = map(int, np.clip(np.round(ir_pt[:2]), [0, 0], [ir_w - 1, ir_h - 1]))
    rgb_x, rgb_y = map(int, np.clip(np.round(rgb_pt[:2]), [0, 0], [rgb_w - 1, rgb_h - 1]))

    if (
        0 <= rgb_x < rgb_w and 0 <= rgb_y < rgb_h and
        0 <= ir_x < ir_w and 0 <= ir_y < ir_h and
        gray_ir[ir_y, ir_x] > threshold
    ):
        warped_ir[rgb_y, rgb_x] = ir_heatmap[ir_y, ir_x]
        mask[rgb_y, rgb_x] = True

# Fill unmasked areas with grayscale
warped_ir[~mask] = rgb_gray_stack[~mask]

# Final overlay
overlay = ((0.5 * warped_ir + 0.5 * rgb_gray_stack)).astype(np.uint8)

# Save outputs
Image.fromarray(warped_ir).save("warped_ir_thresholded.png")
Image.fromarray(overlay).save("overlay_ir_rgb_grayscale_bg.png")

# Display overlay
plt.figure(figsize=(10, 8))
plt.imshow(overlay)
plt.title("Overlay: Inferno IR Heatmap on Grayscale RGB (Thresholded)")
plt.axis("off")
plt.tight_layout()
plt.show()