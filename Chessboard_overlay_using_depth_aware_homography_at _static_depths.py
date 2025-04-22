import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_corners(file_path):
    """
    Load corner points from a text file.

    Each line of the file should contain a comma-separated pair of floats: x,y
    Returns:
        np.ndarray of shape (N, 2)
    """
    with open(file_path, 'r') as f:
        corners = [list(map(float, line.strip().split(','))) for line in f]
    return np.array(corners, dtype=np.float32)

def overlay_images_with_corner_dots(depth):
    """
    Overlay Blaze, IR, and RGB images based on chessboard corner alignment.
    Applies homography transformations and visualizes matching dots in the same frame.

    Args:
        depth (int): Depth label for loading appropriate image and corner files.
    """
    # File paths based on depth
    blaze_file = f"blaze{depth}.tiff"
    ir_file = f"ir{depth}.tif"
    rgb_file = f"rgb{depth}.tif"
    cornersB_file = f"blaze{depth}.txt"
    cornersI_file = f"ir{depth}.txt"
    cornersR_file = f"rgb{depth}.txt"

    # Load chessboard corners
    corners_b = load_corners(cornersB_file)
    corners_i = load_corners(cornersI_file)
    corners_r = load_corners(cornersR_file)

    # Load images
    blaze = cv2.imread(blaze_file)
    ir = cv2.imread(ir_file)
    rgb = cv2.cvtColor(cv2.imread(rgb_file), cv2.COLOR_BGR2RGB)

    size = (blaze.shape[1], blaze.shape[0])  # (width, height)

    # Calculate homographies to map IR and RGB to Blaze frame
    H_ir_to_blaze, _ = cv2.findHomography(corners_i, corners_b)
    H_rgb_to_blaze, _ = cv2.findHomography(corners_r, corners_b)

    # Warp IR and RGB images
    warped_ir = cv2.warpPerspective(ir, H_ir_to_blaze, size)
    warped_rgb = cv2.warpPerspective(rgb, H_rgb_to_blaze, size)

    # Convert to grayscale and normalize
    blaze_gray = cv2.normalize(cv2.cvtColor(blaze, cv2.COLOR_BGR2GRAY), None, 0, 255, cv2.NORM_MINMAX)
    ir_gray = cv2.normalize(cv2.cvtColor(warped_ir, cv2.COLOR_BGR2GRAY), None, 0, 255, cv2.NORM_MINMAX)
    rgb_gray = cv2.normalize(cv2.cvtColor(warped_rgb, cv2.COLOR_RGB2GRAY), None, 0, 255, cv2.NORM_MINMAX)

    # Create RGB-tinted grayscale layers
    blaze_layer = cv2.merge([blaze_gray, np.zeros_like(blaze_gray), np.zeros_like(blaze_gray)])  # Red
    ir_layer = cv2.merge([np.zeros_like(ir_gray), ir_gray, np.zeros_like(ir_gray)])              # Green
    rgb_layer = cv2.merge([np.zeros_like(rgb_gray), np.zeros_like(rgb_gray), rgb_gray])          # Blue

    # Overlay the three channels
    overlay = cv2.addWeighted(blaze_layer, 1.0, ir_layer, 1.0, 0)
    overlay = cv2.addWeighted(overlay, 1.0, rgb_layer, 1.0, 0)

    # Transform corner points to Blaze frame
    corners_i_to_b = cv2.perspectiveTransform(corners_i.reshape(-1, 1, 2), H_ir_to_blaze).reshape(-1, 2)
    corners_r_to_b = cv2.perspectiveTransform(corners_r.reshape(-1, 1, 2), H_rgb_to_blaze).reshape(-1, 2)

    # Draw chessboard corners on overlay
    for pt in corners_b.astype(int):
        cv2.circle(overlay, tuple(pt), radius=2, color=(255, 0, 0), thickness=-1)  # Blue (Blaze)
    for pt in corners_i_to_b.astype(int):
        cv2.circle(overlay, tuple(pt), radius=2, color=(0, 255, 0), thickness=-1)  # Green (IR)
    for pt in corners_r_to_b.astype(int):
        cv2.circle(overlay, tuple(pt), radius=2, color=(0, 0, 255), thickness=-1)  # Red (RGB)

    # Display the final overlay
    plt.figure(figsize=(10, 8))
    plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
    plt.title(f"Overlay at {depth} cm with Chessboard Dots")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def main():
    """
    Entry point for running the script interactively.
    """
    try:
        depth = int(input("Enter depth (e.g., 50, 100, 150, 200): "))
        overlay_images_with_corner_dots(depth)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
