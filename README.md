# Depth-Aware-RGB-and-IR-Image-Alignment-Using-ToF-Based-Homography-Interpolation

This repository contains Python scripts for computing depth-dependent homography transformations between camera views—specifically from IR to ToF and from RGB to ToF. These transformations help align views captured from different sensors when the scene is observed at varying depths.

## Goal

To accurately map points between camera views (such as RGB and ToF), we compute a homography matrix that depends on depth. Since calibration patterns like a chessboard can be observed at different distances, we use this to estimate how the mapping changes with depth.

We assume that each element of the homography matrix varies linearly with depth. So, we compute homographies at two known depths and fit a linear model for each element.

In our case, we captured chessboard images at 100 cm, 150 cm, 200 cm, and 250 cm.
However, to fit a linear model for each homography element, we selected the two depths: 100 cm and 250 cm. This provides a wider range for interpolation and simplifies the model to a first-order approximation.

## Scripts

### Find_chessboard_corners.py
This script detects 2D chessboard corners in input images. It:
- Works with RGB, IR, or ToF images.
- Saves the corner coordinates in text files.
- Should be run first, before computing homographies.
  
### Find_chessbaord_using_adaptive_treshold.py

Interactive tool for tuning thresholding and detecting chessboard corners in IR images.

**Controls:**
- `Trackbars`: Adjust intensity thresholds
- `Enter`: Detect corners
- `s`: Save detected image and corners to file
- `q` or `ESC`: Quit

### RGB_ToF_linear_homography.py
This script computes a linear depth-dependent homography from **ToF to RGB** using the corner points at two depths (100 cm and 250 cm in our case). It:
- Loads corner files for RGB and ToF.
- Computes homographies at both depths.
- Fits a linear model for each matrix element:  
  H_ij(depth) = a + b * depth
- Saves all 9 equations (from the 3×3 homography matrix) to "linear_depth_homography.txt".

### IR_ToF_linear_homography.py
This script works exactly like the RGB version, but instead calculates homographies from **ToF to IR**. It follows the same steps:
- Load corner points for IR and ToF.
- Compute homographies at 100 cm and 250 cm.
- Fit linear models and save them to "linear_depth_homography.txt".

### Chessboard_overlay_using_depth_aware_homography_at _static_depths.py

This visualization script helps validate the homography alignment at a specific depth.
- Loads Blaze (ToF), IR, and RGB images for the selected depth.
- Loads corresponding chessboard corners.
- Computes homographies from IR and RGB to the Blaze frame.
- Warps IR and RGB onto the Blaze image.
- Creates a color-coded overlay:
  - Red: RGB
  - Green: IR
  - Blue: Blaze

- Also overlays chessboard dots:
  - Blaze (reference)
  - IR corners (after transformation)
  - RGB corners (after transformation)

 
### homography_matrix_vs_depth_plot.py

Visualizes how each element of the 3×3 homography matrix changes with depth.

- Loads chessboard corner data for Blaze (reference), IR, and RGB
- Computes homographies: IR → Blaze and RGB → Blaze
- Plots each matrix element (H11–H33) across multiple depths
- Overlay includes:
    - Green dots: IR homography values
    - Red squares: RGB homography values
    - Dashed lines show linear trends
- Saves and displays the plot as 'homography_plot.png'

### combine_checkerboard_corners.py

 Combines multiple 2D chessboard corner files into one file per camera type (Blaze, IR, RGB).
 
- Merges 5 input files per camera
- Adds a comment header for each source file
- Outputs:
     - combined_cornersB.txt
     - combined_cornersI.txt
     - combined_cornersR.txt

### Graph_H_matrix_elements.py

Visualizes how each element of the 3×3 homography matrix changes with depth for IR and RGB images aligned to a base reference.

Input Files
- combined_cornersB.txt — Base image corners  
- combined_cornersI.txt — IR image corners  
- combined_cornersR.txt — RGB image corners  

Each file must contain comma-separated 2D points, grouped by depth (e.g., 42 points per depth).

Output
- homography_plot.png — 9-panel plot showing matrix elements vs. depth


## How to Use

1. Capture chessboard images at multiple known depths (e.g., 100 cm and 250 cm).
2. Run "Find_chessboard_corners.py" to extract and save 2D corner coordinates.
3. Run one of the homography scripts depending on your camera pair:
   - "RGB_ToF_linear_homography.py" for RGB and ToF alignment.
   - "IR_ToF_linear_homography.py" for IR and ToF alignment.
4. The script will ask you to enter the two depths used (100 and 250 in our case).
5. It will generate a file with equations that define how each homography matrix element changes with depth.

## Output

Each script produces a file called "linear_depth_homography.txt" that looks like this:
