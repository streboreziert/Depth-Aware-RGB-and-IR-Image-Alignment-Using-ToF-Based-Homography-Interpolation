import struct
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image
import matplotlib.pyplot as plt

# Set file paths
ply_path = "blaze.ply"
output_txt = "row_col_z.txt"
interp_output = "interpolated_z.txt"
mapping_txt = "depth_to_ir_rgb_mapping.txt"
rgb_img_path = "rgb.tif"
ir_img_path = "ir.tif"

# Image and sensor dimensions
width, height = 640, 480
ir_w, ir_h = 320, 240
rgb_w, rgb_h = 1024, 760

# Define binary format of each vertex: x, y, z, r, g, b
vertex_format = '<fffBBB'
vertex_size = struct.calcsize(vertex_format)

# Function to find where binary data starts in PLY file
def find_data_start(file_path):
    with open(file_path, 'rb') as f:
        while True:
            if f.readline().strip() == b'end_header':
                return f.tell()

# Get offset to binary data
data_start = find_data_start(ply_path)

# Read depth points from the .ply file
depth_points = []
with open(ply_path, 'rb') as f:
    f.seek(data_start)
    for i in range(width * height):
        chunk = f.read(vertex_size)
        if len(chunk) < vertex_size:
            break
        _, _, z, _, _, _ = struct.unpack(vertex_format, chunk)
        row = i // width + 1
        col = i % width + 1
        depth_points.append((row, col, z))

# Save raw depth values to text file
np.savetxt(output_txt, depth_points, fmt="%d %d %.6f", header="row col z", comments='')

# Load depth values into z_map (image grid)
data = np.loadtxt(output_txt, skiprows=1)
z_map = np.full((height, width), np.nan)
for row, col, z in data:
    r, c = int(row) - 1, int(col) - 1
    z_map[r, c] = z

# Filter out outliers using 1st and 99th percentile
valid = z_map[~np.isnan(z_map) & (z_map != 0)]
z_min, z_max = np.percentile(valid, [1, 99])
z_map = np.where(((z_map >= z_min) & (z_map <= z_max)) | (z_map == 0), z_map, np.nan)

# Perform edge-aware interpolation to fill holes in z_map
def edge_aware_interpolation(z_map, spatial_sigma=1.0, depth_sigma=0.1, window_size=3):
    padded = np.pad(z_map, pad_width=window_size//2, mode='reflect')
    output = np.full_like(z_map, np.nan)

    grid = np.arange(window_size) - window_size // 2
    yy, xx = np.meshgrid(grid, grid)
    spatial_weights = np.exp(-(xx**2 + yy**2) / (2 * spatial_sigma**2))

    for r in range(z_map.shape[0]):
        for c in range(z_map.shape[1]):
            if z_map[r, c] == 0:
                output[r, c] = 0
                continue

            patch = padded[r:r+window_size, c:c+window_size]
            center_val = z_map[r, c]

            if np.isnan(center_val):
                if np.isnan(patch).all():
                    center_val = 0
                else:
                    center_val = np.nanmean(patch)

            depth_diff = patch - center_val
            depth_weights = np.exp(-(depth_diff ** 2) / (2 * depth_sigma**2))
            combined_weights = spatial_weights * depth_weights
            combined_weights[np.isnan(patch)] = 0

            if np.sum(combined_weights) > 0:
                output[r, c] = np.nansum(patch * combined_weights) / np.sum(combined_weights)
            else:
                output[r, c] = center_val

    return output

# Interpolate and fill missing values
z_interp = edge_aware_interpolation(z_map, spatial_sigma=1.0, depth_sigma=0.05)
if np.isnan(z_interp).any():
    nan_mask = np.isnan(z_interp)
    nearest_idx = distance_transform_edt(nan_mask, return_indices=True)
    nearest_idx = tuple(arr.astype(int) for arr in nearest_idx)
    z_filled = z_interp[nearest_idx]
else:
    z_filled = z_interp

# Save interpolated depth to file
out_data = [(r + 1, c + 1, z_filled[r, c]) for r in range(height) for c in range(width)]
np.savetxt(interp_output, out_data, fmt="%d %d %.6f", header="row col z", comments='')

# Define homography coefficients as functions of depth
ir_coeffs = {
    'H11': (1.07204, -0.00005), 'H12': (-0.10841, -0.00062), 'H13': (157.342, 0.084),
    'H21': (0.02877, 0.00004),  'H22': (0.96821, -0.00071), 'H23': (51.135, 0.227),
    'H31': (0.00008, 0.0000003),'H32': (-0.00041, -0.0000017), 'H33': (1.0, 0.0)
}
rgb_coeffs = {
    'H11': (0.26969, 0.00031), 'H12': (0.00174, -0.00031), 'H13': (172.811, 0.025),
    'H21': (-0.03179, 0.00021), 'H22': (0.31907, -0.00017), 'H23': (110.336, 0.167),
    'H31': (-0.00016, 0.0000009), 'H32': (0.000014, -0.0000009), 'H33': (1.0, 0.0)
}

# Compute homography matrix H based on depth in cm
def get_H(coeffs, d_cm):
    return np.array([
        [coeffs['H11'][0] + coeffs['H11'][1]*d_cm, coeffs['H12'][0] + coeffs['H12'][1]*d_cm, coeffs['H13'][0] + coeffs['H13'][1]*d_cm],
        [coeffs['H21'][0] + coeffs['H21'][1]*d_cm, coeffs['H22'][0] + coeffs['H22'][1]*d_cm, coeffs['H23'][0] + coeffs['H23'][1]*d_cm],
        [coeffs['H31'][0] + coeffs['H31'][1]*d_cm, coeffs['H32'][0] + coeffs['H32'][1]*d_cm, coeffs['H33'][0]]
    ])

# Map each depth pixel to IR and RGB coordinates
depth = np.loadtxt(interp_output, skiprows=1)
mapped = []
for row, col, z in depth:
    pt = np.array([col, row, 1])
    d_cm = -z / 10.0 if z != 0 else 0

    ir_pt = np.linalg.inv(get_H(ir_coeffs, d_cm)) @ pt
    rgb_pt = np.linalg.inv(get_H(rgb_coeffs, d_cm)) @ pt
    ir_pt /= ir_pt[2]
    rgb_pt /= rgb_pt[2]

    ir_x, ir_y = map(int, np.clip(np.round(ir_pt[:2]), [0, 0], [ir_w - 1, ir_h - 1]))
    rgb_x, rgb_y = map(int, np.clip(np.round(rgb_pt[:2]), [0, 0], [rgb_w - 1, rgb_h - 1]))

    mapped.append((int(row), int(col), z, ir_x, ir_y, rgb_x, rgb_y))

# Save depth-to-image mapping
np.savetxt(mapping_txt, mapped, fmt="%d %d %.2f %d %d %d %d",
           header="row col depth_mm IR_x IR_y RGB_x RGB_y", comments='')

# Load IR and RGB images
rgb_img = np.array(Image.open(rgb_img_path).convert("RGB"))
ir_img = np.array(Image.open(ir_img_path).convert("RGB"))
warped_ir = np.zeros_like(rgb_img)
mask = np.zeros(rgb_img.shape[:2], dtype=bool)

# Warp IR image onto RGB image space using pixel mapping
mapping = np.loadtxt(mapping_txt, skiprows=1)
for entry in mapping:
    _, _, _, ir_x, ir_y, rgb_x, rgb_y = map(int, entry)
    if 0 <= rgb_x < rgb_w and 0 <= rgb_y < rgb_h and 0 <= ir_x < ir_w and 0 <= ir_y < ir_h:
        warped_ir[rgb_y, rgb_x] = ir_img[ir_y, ir_x]
        mask[rgb_y, rgb_x] = True

# Fill any gaps in the warped image using nearest-neighbor inpainting
if not np.all(mask):
    dist, idx = distance_transform_edt(~mask, return_indices=True)
    idx = tuple(arr.astype(int) for arr in idx)
    warped_ir[~mask] = warped_ir[idx[0][~mask], idx[1][~mask]]

# Save the warped IR image
Image.fromarray(warped_ir).save("warped_ir_aligned_to_rgb.png")

# Crop region for visualization
y_start, y_end = 0, 570
x_start, x_end = 0, 1000
cropped_ir = warped_ir[y_start:y_end, x_start:x_end]
cropped_rgb = rgb_img[y_start:y_end, x_start:x_end]

# Display side-by-side IR and RGB images
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))
ax1.imshow(cropped_ir)
ax1.set_title("IR aligned to RGB (cropped)")
ax1.axis("off")
ax2.imshow(cropped_rgb)
ax2.set_title("Original RGB (cropped)")
ax2.axis("off")
plt.tight_layout()
fig.savefig("cropped_side_by_side_ir_rgb.png", dpi=300, bbox_inches='tight')
plt.show()
