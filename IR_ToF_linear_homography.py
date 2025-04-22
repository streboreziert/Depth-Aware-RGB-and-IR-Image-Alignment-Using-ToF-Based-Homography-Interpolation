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

# Load corner points for Blaze and IR cameras
cornersBlaze = load_corners_by_depth("combined_cornersB.txt")
cornersIR = load_corners_by_depth("combined_cornersI.txt")

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
        ptsIR_1, ptsIR_2 = cornersIR[idx_1], cornersIR[idx_2]
        ptsBlaze_1, ptsBlaze_2 = cornersBlaze[idx_1], cornersBlaze[idx_2]

        # Compute homographies from IR to Blaze at both depths
        H_1, _ = cv2.findHomography(ptsIR_1, ptsBlaze_1)
        H_2, _ = cv2.findHomography(ptsIR_2, ptsBlaze_2)

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
            f.write("### IR to Blaze Homography Coefficients ###\n")
            for idx, (b, a) in enumerate(coeffs):
                i, j = divmod(idx, 3)
                f.write(f"H{i+1}{j+1}(d) = {a:.10f} + {b:.10f} * d\n")

        print("Saved homography model from IR to Blaze to 'linear_depth_homography_IR_ToF.txt'")
