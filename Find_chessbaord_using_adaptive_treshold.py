import cv2
import numpy as np

# Load infrared image in grayscale
image = cv2.imread('ir150.tif', cv2.IMREAD_GRAYSCALE)

# Define inner corners of the chessboard pattern (rows, columns)
chessboard_size = (7, 6)

# Placeholder function for trackbar callback
def nothing(x):
    pass

# Create OpenCV window and trackbars for threshold tuning
cv2.namedWindow("Threshold + Chessboard Detection")
cv2.createTrackbar("Lower", "Threshold + Chessboard Detection", 50, 255, nothing)
cv2.createTrackbar("Upper", "Threshold + Chessboard Detection", 200, 255, nothing)

# Initialize variables
corners = None
found = False
result_image = None
display_chessboard = False

# Track last threshold values to detect changes
last_t1 = cv2.getTrackbarPos("Lower", "Threshold + Chessboard Detection")
last_t2 = cv2.getTrackbarPos("Upper", "Threshold + Chessboard Detection")

# Main loop
while True:
    # Get updated threshold values
    t1 = cv2.getTrackbarPos("Lower", "Threshold + Chessboard Detection")
    t2 = cv2.getTrackbarPos("Upper", "Threshold + Chessboard Detection")
    t1, t2 = min(t1, t2), max(t1, t2)

    # Apply manual thresholding
    thresh_img = np.zeros_like(image)
    thresh_img[(image >= t1) & (image <= t2)] = 127
    thresh_img[image > t2] = 255

    # Reset preview if threshold values have changed
    if t1 != last_t1 or t2 != last_t2:
        display_chessboard = False
        last_t1, last_t2 = t1, t2

    # Show result with corners if already found
    if display_chessboard and found:
        cv2.imshow("Threshold + Chessboard Detection", result_image)
    else:
        # Show thresholded preview
        preview = cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)
        cv2.imshow("Threshold + Chessboard Detection", preview)

    key = cv2.waitKey(1) & 0xFF

    if key == 13:  # ENTER key pressed
        # Try to detect chessboard corners
        found, corners = cv2.findChessboardCorners(thresh_img, chessboard_size, None)
        result_image = cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)
        if found:
            # Draw corners if found
            cv2.drawChessboardCorners(result_image, chessboard_size, corners, found)
            display_chessboard = True
            print("Found")
        else:
            print("NOT found")

    elif key == ord('s') and found and result_image is not None:
        # Save image with detected corners
        cv2.imwrite("chessboard_detected.png", result_image)
        # Save corners to a text file
        with open("cornersI150.txt", "w") as f:
            for corner in corners:
                x, y = corner.ravel()
                f.write(f"{x:.2f}, {y:.2f}\n")
        print("Saved")

    elif key == ord('q') or key == 27:
        # Quit on 'q' or ESC
        break

# Close OpenCV windows
cv2.destroyAllWindows()
