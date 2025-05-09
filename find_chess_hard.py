import cv2
import numpy as np

image = cv2.imread('ir150.tif', cv2.IMREAD_GRAYSCALE)
chessboard_size = (7, 6)  # inner corners

def nothing(x):
    pass

cv2.namedWindow("Threshold + Chessboard Detection")
cv2.createTrackbar("Lower", "Threshold + Chessboard Detection", 50, 255, nothing)
cv2.createTrackbar("Upper", "Threshold + Chessboard Detection", 200, 255, nothing)

corners = None
found = False
result_image = None
display_chessboard = False

last_t1 = cv2.getTrackbarPos("Lower", "Threshold + Chessboard Detection")
last_t2 = cv2.getTrackbarPos("Upper", "Threshold + Chessboard Detection")

while True:
    t1 = cv2.getTrackbarPos("Lower", "Threshold + Chessboard Detection")
    t2 = cv2.getTrackbarPos("Upper", "Threshold + Chessboard Detection")
    t1, t2 = min(t1, t2), max(t1, t2)

    thresh_img = np.zeros_like(image)
    thresh_img[(image >= t1) & (image <= t2)] = 127
    thresh_img[image > t2] = 255

    if t1 != last_t1 or t2 != last_t2:
        display_chessboard = False
        last_t1, last_t2 = t1, t2

    if display_chessboard and found:
        cv2.imshow("Threshold + Chessboard Detection", result_image)
    else:
        preview = cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)
        cv2.imshow("Threshold + Chessboard Detection", preview)

    key = cv2.waitKey(1) & 0xFF

    if key == 13: 
        found, corners = cv2.findChessboardCorners(thresh_img, chessboard_size, None)
        result_image = cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)
        if found:
            cv2.drawChessboardCorners(result_image, chessboard_size, corners, found)
            display_chessboard = True
            print("Found")
        else:
            print("NOT found")

    elif key == ord('s') and found and result_image is not None:
        cv2.imwrite("chessboard_detected.png", result_image)
        with open("cornersI150.txt", "w") as f:
            for corner in corners:
                x, y = corner.ravel()
                f.write(f"{x:.2f}, {y:.2f}\n")
        print("Saved")

    elif key == ord('q') or key == 27:
        break

cv2.destroyAllWindows()