import numpy as np
import matplotlib.pyplot as plt
import cv2

# Depths in cm for each chessboard capture set
DEPTHS = [100, 150, 200, 250]

# Number of chessboard corners per capture
POINTS_PER_DEPTH = 42

# Labels for each homography matrix element (flattened 3x3 matrix)
labels = [f"H{i // 3 + 1}{i % 3 + 1}" for i in range(9)]

# Function to load and group corner points by depth
def load_corners(filepath):
    with open(filepath, 'r') as f:
        # Read lines that are not comments or empty
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    # Convert to float32 array
    points = np.array([list(map(float, line.split(","))) for line in lines], dtype=np.float32)
    
    # Split into groups based on number of points per depth
    return np.array_split(points, len(points) // POINTS_PER_DEPTH)

# Main function to plot homography matrix element trends across depths
def plot_homography_matrix(cornersB_path, cornersI_path, cornersR_path, save_path="homography_plot.png"):
    # Load corner data from files
    corners_b = load_corners(cornersB_path)
    corners_i = load_corners(cornersI_path)
    corners_r = load_corners(cornersR_path)

    # Compute homographies: IR → Base and RGB → Base
    H_ir = [cv2.findHomography(i, b)[0].flatten() for i, b in zip(corners_i, corners_b)]
    H_rgb = [cv2.findHomography(r, b)[0].flatten() for r, b in zip(corners_r, corners_b)]

    # Convert lists to NumPy arrays
    H_ir = np.array(H_ir)
    H_rgb = np.array(H_rgb)

    # Create 3x3 subplot grid (9 elements in homography matrix)
    fig, axs = plt.subplots(3, 3, figsize=(14, 10))
    axs = axs.ravel()

    for i in range(9):
        ax = axs[i]
        x = np.array(DEPTHS)  # x-axis: depth
        y_ir = H_ir[:, i]     # y-axis for IR-to-Base
        y_rgb = H_rgb[:, i]   # y-axis for RGB-to-Base

        # Plot points for IR and RGB homographies
        ax.plot(x, y_ir, 'o', label='IR points', color='green')
        ax.plot(x, y_rgb, 's', label='RGB points', color='red')

        # Plot dashed lines connecting start and end points
        ax.plot([x[0], x[-1]], [y_ir[0], y_ir[-1]], '--', label='IR line', color='lime')
        ax.plot([x[0], x[-1]], [y_rgb[0], y_rgb[-1]], '--', label='RGB line', color='orange')

        # Add title and axis labels
        ax.set_title(labels[i])
        ax.set_xlabel("Depth (cm)")
        ax.set_ylabel("Value")
        ax.grid(True)
        ax.legend(fontsize=7)

    # Set the overall figure title and adjust layout
    plt.suptitle("Homography Matrix Elements vs Depth", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    # Save the resulting figure
    plt.savefig(save_path, dpi=300)
    plt.show()

# Example usage: load data and plot
plot_homography_matrix("combined_cornersB.txt", "combined_cornersI.txt", "combined_cornersR.txt")
