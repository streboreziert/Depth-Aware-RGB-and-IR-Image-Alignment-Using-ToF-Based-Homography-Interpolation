import numpy as np
import matplotlib.pyplot as plt
import cv2

# === CONFIGURATION ===
# Depth values in centimeters for which homographies are computed
DEPTHS = [100, 150, 200, 250]

# Number of corner points per depth (e.g., 6x7 checkerboard = 42)
POINTS_PER_DEPTH = 42

# Labels for the 3x3 homography matrix elements
labels = [f"H{i // 3 + 1}{i % 3 + 1}" for i in range(9)]


def load_corners(filepath):
    """
    Loads corner coordinates from a text file.
    Each line should contain two comma-separated values: x, y.
    Returns a list of point arrays, one per depth.
    """
    with open(filepath, 'r') as f:
        # Filter out empty lines and comments
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    # Convert lines into a NumPy array of shape (total_points, 2)
    points = np.array([list(map(float, line.split(","))) for line in lines], dtype=np.float32)

    # Split into chunks corresponding to each depth
    return np.array_split(points, len(points) // POINTS_PER_DEPTH)


def plot_homography_matrix(cornersB_path, cornersI_path, cornersR_path, save_path="homography_plot.png"):
    """
    Loads corner data for Base, IR, and RGB images at multiple depths.
    Computes the homographies IR -> Base and RGB -> Base.
    Plots how each homography matrix element changes with depth.
    """
    # Load corner points for each modality
    corners_b = load_corners(cornersB_path)
    corners_i = load_corners(cornersI_path)
    corners_r = load_corners(cornersR_path)

    # Compute homographies for each depth
    H_ir = [cv2.findHomography(i, b)[0].flatten() for i, b in zip(corners_i, corners_b)]
    H_rgb = [cv2.findHomography(r, b)[0].flatten() for r, b in zip(corners_r, corners_b)]

    # Convert to NumPy arrays of shape (num_depths, 9)
    H_ir = np.array(H_ir)
    H_rgb = np.array(H_rgb)

    # Create subplots for each homography element
    fig, axs = plt.subplots(3, 3, figsize=(14, 10))
    axs = axs.ravel()

    for i in range(9):
        ax = axs[i]

        # x-axis: depths, y-axis: homography values
        x = np.array(DEPTHS)
        y_ir = H_ir[:, i]
        y_rgb = H_rgb[:, i]

        # Plot discrete points
        ax.plot(x, y_ir, 'o', label='IR points', color='green')
        ax.plot(x, y_rgb, 's', label='RGB points', color='red')

        # Plot connecting lines between first and last depth
        ax.plot([x[0], x[-1]], [y_ir[0], y_ir[-1]], '--', label='IR line', color='lime')
        ax.plot([x[0], x[-1]], [y_rgb[0], y_rgb[-1]], '--', label='RGB line', color='orange')

        ax.set_title(labels[i])
        ax.set_xlabel("Depth (cm)")
        ax.set_ylabel("Homography Value")
        ax.grid(True)
        ax.legend(fontsize=7)

    # Global title and layout
    plt.suptitle("Homography Matrix Elements vs Depth", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    # Save and show the figure
    plt.savefig(save_path, dpi=300)
    plt.show()


# === USAGE EXAMPLE ===
# Provide paths to the checkerboard corner files for Base, IR, and RGB
plot_homography_matrix(
    "combined_cornersB.txt",
    "combined_cornersI.txt",
    "combined_cornersR.txt"
)
