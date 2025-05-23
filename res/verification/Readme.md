**Note on Object Detection Thresholds and Calibration**

- The threshold for red object detection must be adjusted **per image**, as lighting and exposure vary between shots.
- For the **100 cm image**, the **"close" Basler Blaze camera setting** was used.
- Because of this setting change, a **separate calibration matrix** is required.

Calibration data from other camera modes (e.g., long-range) should **not** be reused for short-distance measurements, as it may lead to inaccurate results.
