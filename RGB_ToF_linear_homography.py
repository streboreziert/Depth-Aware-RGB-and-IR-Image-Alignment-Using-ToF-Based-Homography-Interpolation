import numpy as np
import cv2

# Number of chessboard corners per depth (e.g., 6x7 grid = 42)
POINTS_PER_DEPTH = 42

# The list of depths (in cm) used when capturing the data
DEPTHS = [100, 150, 200, 250]

def load_corners_by_depth(filepath):
    """
    Reads 2D corner coordinates from a text file.
    Each depth level has the same number of corner points (e.g., 42).
    This function splits all the loaded points into separate groups — one group for each depth.
    """
    with open(filepath, 'r') as f:
        lines = [
            list(map(float, line.strip().split(',')))
            for line in f
            if line.strip() and not line.startswith('#')  # ignore empty lines and comments
        ]
    points = np.array(lines, dtype=np.float32)
    return np.array_split(points, len(points) // POINTS_PER_DEPTH)

# Load corner points for RGB and ToF (e.g., Blaze camera)
cornersRGB = load_corners_by_depth("combined_cornersR.txt")
cornersToF = load_corners_by_depth("combined_cornersB.txt")

# Show available depths and ask the user to pick two
print("Available depths:", DEPTHS)
depth_1 = int(input("Enter the first depth: "))

# Check if the input is valid
if depth_1 not in DEPTHS:
    print("Error: First depth is not valid.")
else:
    depth_2 = int(input("Enter the second depth: "))
    
    if depth_2 not in DEPTHS:
        print("Error: Second depth is not valid.")
    else:
        # Get the index of each selected depth
        idx_1 = DEPTHS.index(depth_1)
        idx_2 = DEPTHS.index(depth_2)
        depth_vals = np.array([depth_1, depth_2])

        # Get the corresponding corner points at each depth
        ptsToF_1, ptsToF_2 = cornersToF[idx_1], cornersToF[idx_2]
        ptsRGB_1, ptsRGB_2 = cornersRGB[idx_1], cornersRGB[idx_2]

        # Compute homographies from ToF to RGB at both depths
        H_1, _ = cv2.findHomography(ptsToF_1, ptsRGB_1)
        H_2, _ = cv2.findHomography(ptsToF_2, ptsRGB_2)

        # Fit a linear model for each homography matrix element:
        # H_ij(depth) = a + b * depth
        H_1_flat = H_1.flatten()
        H_2_flat = H_2.flatten()
        coeffs = np.array([
            np.polyfit(depth_vals, [H_1_flat[i], H_2_flat[i]], 1)
            for i in range(9)
        ])  # shape: (9, 2) -> [b, a] for each element

        # Save the linear equations to a file
        with open("linear_depth_homography.txt", "w") as f:
            for idx, (b, a) in enumerate(coeffs):
                i, j = divmod(idx, 3)
                f.write(f"H{i+1}{j+1}(d) = {a:.10f} + {b:.10f} * d\n")

        print(" Saved homography model from ToF to RGB to 'linear_depth_homography.txt'")
