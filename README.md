# Depth-Aware-RGB-and-IR-Image-Alignment-Using-ToF-Based-Homography-Interpolation

This repository contains Python scripts for computing depth-dependent homography transformations between camera views—specifically from IR to ToF and from RGB to ToF. These transformations help align views captured from different sensors when the scene is observed at varying depths.

## Goal

To accurately map points between camera views (such as RGB and ToF), we compute a homography matrix that depends on depth. Since calibration patterns like a chessboard can be observed at different distances, we use this to estimate how the mapping changes with depth.

We assume that each element of the homography matrix varies linearly with depth. So, we compute homographies at two known depths and fit a linear model for each element.

In our case, we captured chessboard images at 100 cm, 150 cm, 200 cm, and 250 cm.
However, to fit a linear model for each homography element, we selected the two extreme depths: 100 cm and 250 cm. This provides a wider range for interpolation and simplifies the model to a first-order approximation.

## Scripts

### `Find_chessboard_corners.py`
This script detects 2D chessboard corners in input images. It:
- Works with RGB, IR, or ToF images.
- Saves the corner coordinates in text files.
- Should be run first, before computing homographies.

### `RGB_ToF_linear_homography.py`
This script computes a linear depth-dependent homography from **ToF to RGB** using the corner points at two depths (100 cm and 250 cm in our case). It:
- Loads corner files for RGB and ToF.
- Computes homographies at both depths.
- Fits a linear model for each matrix element:  
  H_ij(depth) = a + b * depth
- Saves all 9 equations (from the 3×3 homography matrix) to "linear_depth_homography.txt".

### `IR_ToF_linear_homography.py`
This script works exactly like the RGB version, but instead calculates homographies from **ToF to IR**. It follows the same steps:
- Load corner points for IR and ToF.
- Compute homographies at 100 cm and 250 cm.
- Fit linear models and save them to "linear_depth_homography.txt".

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
