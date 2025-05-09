import numpy as np
import matplotlib.pyplot as plt
import cv2

# === CONFIG ===
DEPTHS = [100, 150, 200, 250]
POINTS_PER_DEPTH = 42
labels = [f"H{i//3+1}{i%3+1}" for i in range(9)]

def load_corners(filepath):
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line and not line.startswith("#")]
    points = np.array([list(map(float, line.split(","))) for line in lines], dtype=np.float32)
    return np.array_split(points, len(points) // POINTS_PER_DEPTH)

# === MAIN FUNCTION ===
def plot_homography_matrix(cornersB_path, cornersI_path, cornersR_path, save_path="homography_plot.png"):
    # Load corner data
    corners_b = load_corners(cornersB_path)
    corners_i = load_corners(cornersI_path)
    corners_r = load_corners(cornersR_path)

    # Compute homographies
    H_ir = [cv2.findHomography(i, b)[0].flatten() for i, b in zip(corners_i, corners_b)]
    H_rgb = [cv2.findHomography(r, b)[0].flatten() for r, b in zip(corners_r, corners_b)]

    H_ir = np.array(H_ir)
    H_rgb = np.array(H_rgb)

    # Plotting
    fig, axs = plt.subplots(3, 3, figsize=(14, 10))
    axs = axs.ravel()

    for i in range(9):
        ax = axs[i]
        x = np.array(DEPTHS)
        y_ir = H_ir[:, i]
        y_rgb = H_rgb[:, i]

        # Plot points
        ax.plot(x, y_ir, 'o', label='IR points', color='green')
        ax.plot(x, y_rgb, 's', label='RGB points', color='red')

        # Draw straight lines from 100 to 250 cm
        ax.plot([x[0], x[-1]], [y_ir[0], y_ir[-1]], '--', label='IR line', color='lime')
        ax.plot([x[0], x[-1]], [y_rgb[0], y_rgb[-1]], '--', label='RGB line', color='orange')

        ax.set_title(labels[i])
        ax.set_xlabel("Depth (cm)")
        ax.set_ylabel("Value")
        ax.grid(True)
        ax.legend(fontsize=7)

    plt.suptitle("Homography Matrix Elements vs Depth", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    # Save the figure
    plt.savefig(save_path, dpi=300)
    plt.show()

# === EXAMPLE USAGE ===
plot_homography_matrix("combined_cornersB.txt", "combined_cornersI.txt", "combined_cornersR.txt")