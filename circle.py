import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def process_image(image_path, label, output_img_name):
    # Load image in grayscale
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        print(f"❌ Error: Could not load {image_path}")
        return [], None

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detect circles using Hough Transform
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=50,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=100
    )

    # Convert grayscale to color for visualization
    output = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    results = []

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for i, (x, y, r) in enumerate(circles):
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)
            cv2.putText(output, str(i + 1), (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            results.append((label, i + 1, x, y, r))
            print(f"{label} Circle {i+1}: Center = ({x}, {y}), Radius = {r}")
    else:
        print(f"⚠️ No circles detected in {label} image.")

    # Save the output image
    cv2.imwrite(output_img_name, output)

    return results, output

# --- MAIN PROCESS ---

# File paths
ir_image = "ir.png"
rgb_image = "rgb.png"
ir_output = "ir_circles.png"
rgb_output = "rgb_circles.png"

# Process both images
ir_results, ir_vis = process_image(ir_image, "IR", ir_output)
rgb_results, rgb_vis = process_image(rgb_image, "RGB", rgb_output)

# Combine and save results
all_results = ir_results + rgb_results
print(f"\n✅ Total circles detected: {len(all_results)}")

if all_results:
    all_results_array = np.array(all_results, dtype=object)
    np.savetxt("detected_circles.txt", all_results_array, fmt="%s %d %d %d %d",
               header="Image Circle# Center_X Center_Y Radius", comments='')
    print("✅ Results saved to detected_circles.txt")
else:
    print("⚠️ No circles found to write to file.")

# Visual display
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

if ir_vis is not None:
    axs[0].imshow(cv2.cvtColor(ir_vis, cv2.COLOR_BGR2RGB))
    axs[0].set_title("IR Circles")
    axs[0].axis("off")

if rgb_vis is not None:
    axs[1].imshow(cv2.cvtColor(rgb_vis, cv2.COLOR_BGR2RGB))
    axs[1].set_title("RGB Circles")
    axs[1].axis("off")

plt.tight_layout()
plt.show()