import cv2
import numpy as np

# Load grayscale image
img = cv2.imread("ir.png", cv2.IMREAD_GRAYSCALE)

# Apply Gaussian blur
blurred = cv2.GaussianBlur(img, (5, 5), 0)

# Otsu's thresholding
_, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Find external contours
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if not contours:
    raise Exception("No contours found!")

# Find the largest contour
largest = max(contours, key=cv2.contourArea)

# Compute moments and center of mass
M = cv2.moments(largest)
cX = int(M["m10"] / M["m00"])
cY = int(M["m01"] / M["m00"])
center = (cX, cY)

# Calculate distances from center to each contour point
distances = [np.sqrt((x - cX)**2 + (y - cY)**2) for [[x, y]] in largest]
max_distance = max(distances)
avg_distance = sum(distances) / len(distances)

# Draw results
output = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
cv2.circle(output, center, 5, (0, 0, 255), -1)
cv2.putText(output, "Center", (cX + 10, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

# Optional: draw circle of average shell distance
cv2.circle(output, center, int(avg_distance), (255, 0, 255), 1)
cv2.circle(output, center, int(max_distance), (255, 0, 0), 1)

# Save result
cv2.imwrite("analysis_output.png", output)

# Save results to text file
with open("analysis_results.txt", "w") as f:
    f.write(f"Center: ({cX}, {cY})\n")
    f.write(f"Max distance to contour: {max_distance:.2f} px\n")
    f.write(f"Average distance to contour: {avg_distance:.2f} px\n")
    
# Print results
print(f"Center: ({cX}, {cY})")
print(f"Max distance to contour: {max_distance:.2f} px")
print(f"Average distance to contour: {avg_distance:.2f} px")
