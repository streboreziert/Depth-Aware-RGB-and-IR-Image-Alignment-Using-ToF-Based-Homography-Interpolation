import cv2
import numpy as np
import matplotlib.pyplot as plt

# Set the path to the input image
image_path = "path/to/your/image.tif"

# Define the size of the chessboard (inner corners: columns, rows)
chessboard_size = (7, 6)

# Load the image and convert to grayscale
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Try to detect chessboard corners
ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

if ret:
    # Draw the corners on the image
    cv2.drawChessboardCorners(image, chessboard_size, corners, ret)

    # Save the detected corner coordinates to a text file
    with open("chessboard_corners.txt", "w") as f:
        for point in corners:
            x, y = point.ravel()
            f.write(f"{x:.6f}, {y:.6f}\n")

    print("Corners found.")
    print("Saved to chessboard_corners.txt")
else:
    print("Chessboard not found.")

# Convert BGR to RGB for matplotlib display
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Display the result
plt.figure(figsize=(10, 8))
plt.imshow(image_rgb)
plt.title("Chessboard Detected (7x6)" if ret else "Not Found (7x6)")
plt.axis('off')
plt.show()
