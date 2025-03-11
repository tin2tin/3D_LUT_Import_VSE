# Import .cube LUTs as RGB curves in Blender's Video Sequence Editor (VSE) with optional grayscale conversion


https://github.com/user-attachments/assets/fd3ac91d-c23f-45cf-ac0f-8d0f04d6bccd


## Installation
1. Download the add-on: https://github.com/tin2tin/3D_Lut_Import_VSE/archive/refs/heads/main.zip
2. Open Blender → Edit > Preferences > Add-ons.
3. Install and enable it.
4. Save Preferences. 

## Key Features
1. LUT Import & Application
Batch Process: Applies LUT to all selected non-audio strips in the VSE.
Automatic Overwrite: Replaces existing "LUT RGB Curves" modifiers on strips.
3D LUT Compatibility: Handles cubic .cube LUT files, extracting their diagonal path values for RGB curves.
2. Grayscale Conversion
Desaturation Option: Toggles a Hue Correction modifier to zero saturation while preserving the original LUT’s contrast curves.
(Only saturation of the Hue Correction modifier’s 2nd curve is set to Y=0; hue and value remain untouched.)
3. Seamless Integration
Shortcut Access: Available via the Shift + A Add Menu under Effects > LUT (Cube File).
Diagnostic Reporting: Alerts users about invalid LUT formats or other issues.
4. Technical Enhancements
NP Interpolation: Reduces large LUT datasets to 256 points for stability.
Error-Resistant Parsers: Validates LUT size headers and structure.


## Usage Guide
### Step 1. Prepare Your Scene
Select Strips: Choose non-audio VSE strips (video/image/visual strips).

### Step 2. Import the LUT
Open the Add Menu:
In the VSE, press Shift + A → Navigate to Effects → Click "LUT (Cube File)".

Navigate to your .cube LUT file (e.g., Rec709_to_P3.cube).

Optional: Check Desaturate to convert to grayscale while keeping tonal curves.

The script processes your LUT:
Reduction interpolation (if needed).
Modifier application over selected strips.
Hue modifier with saturation zeroed added if selected (Desaturate is checked).

### Step 3. Modify or Remove LUTs
Overwrite Existing LUTs: Re-run the operator on the same strips – it automatically removes old modifiers.

View Modifiers:
In the VSE Properties Shelf (N), select a strip to see modifiers like "LUT RGB Curves" and "Hue" (if Desaturation is seleceted).


## Requirements
Blender Version: ≥ 3.0 (tested up through 4.x).
LUT Format: Standard .cube files with proper headers, e.g.:
LUT_3D_SIZE 33

## Example Workflow

Standard LUT Application:
Select a clip → Shift-A → Effects → LUT (Cube File) → Choose LUT → Uncheck Desaturate.
Result: Colors adjusted to the LUT’s RGB curves.


## Grayscale Conversion:
Same as above → Check Desaturate.
Result: Desaturated with contrast/preset from LUT, but no color information.
