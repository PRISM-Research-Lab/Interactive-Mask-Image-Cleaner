# Interactive-Mask-Image-Cleaner

An interactive Python tool for manually cleaning and refining image segmentation masks using OpenCV. Users can select regions of interest (ROIs), remove unwanted pixels using a brush or rectangle, and save cleaned masks while preserving their original dimensions and pixel values.

The tool is designed for researchers and students working with image segmentation, plant phenotyping, computer vision, and image annotation.

## 1. Features

- **Keep Rectangle:** Select a rectangular region to preserve. All pixels outside the rectangle become black.
- **Erase Rectangle:** Select a rectangular region to remove. All pixels inside the rectangle become black.
- **Keep Polygon:** Select an irregular region using multiple mouse clicks. Pixels outside the polygon become black.
- **Black Brush:** Manually erase unwanted pixels using an adjustable brush.
- **Undo/Redo:** Correct mistakes during editing.
- **Pixel Analysis:** Display unique pixel values and their counts.
- **Image Preservation:** Maintain original image dimensions and unchanged pixel values in retained regions.
- **Automatic Saving:** Save cleaned masks using the original filename in a designated output folder.

## 2. Requirements

- Python 3.9 or newer
- PyCharm (recommended for beginners)
- OpenCV
- NumPy
- Tkinter (typically included with standard Python installations)

Install the required Python packages:

```bash
pip install opencv-python numpy
```

## 3. Download the Repository

Download the repository from GitHub using **Code → Download ZIP**, then extract the ZIP file.

Alternatively, clone it using Git:

```bash
git clone https://github.com/Computational-Plant-Science/Interactive-Mask-Cleaner.git
```

Open the extracted or cloned project folder in PyCharm.

The repository should contain the following files:

```text
Interactive-Mask-Cleaner/
│
├── interactive_mask_cleaner.py
├── 4041_Control_C2_Day7_002.png
└── README.md
```

The PNG file is an example segmentation mask that students can use to test the program.

## 4. Running the Code in PyCharm

**Step 1: Open the project**

1. Open PyCharm.
2. Select **File → Open**.
3. Navigate to the `Interactive-Mask-Cleaner` folder.
4. Click **OK** or **Open**.

**Step 2: Configure Python**

Make sure PyCharm is using a Python interpreter with `opencv-python` and `numpy` installed.

If these packages are missing, open the PyCharm Terminal and run:

```bash
pip install opencv-python numpy
```

**Step 3: Configure the output folder**

Open `interactive_mask_cleaner.py` and locate:

```python
OUTPUT_FOLDER = r"C:\WVSU_Documents\Research\Scripts\Test_projectV1\Cleaned"
```

For easier reproduction, change it to:

```python
OUTPUT_FOLDER = "Cleaned"
```

The program will automatically create a `Cleaned` folder if it does not exist.

**Step 4: Run the program**

1. Open `interactive_mask_cleaner.py`.
2. Right-click inside the code editor.
3. Select **Run 'interactive_mask_cleaner'**, or click the green Run button.

A file selection window will appear.

**Step 5: Select the example image**

Navigate to the project folder and select:

```text
4041_Control_C2_Day7_002.png
```

Click **Open**.

The image will appear in an interactive OpenCV window.

## 5. Editing the Segmentation Mask

Click the OpenCV image window to activate keyboard controls.

| Key | Function | Description |
|---|---|---|
| `R` | Keep Rectangle | Drag a rectangle; pixels outside become black |
| `E` | Erase Rectangle | Drag a rectangle; pixels inside become black |
| `P` | Keep Polygon | Click points around the region to keep |
| `Enter` | Apply Polygon | Complete the polygon selection |
| `B` | Black Brush | Click and drag to remove unwanted pixels |
| `+` / `-` | Brush Size | Increase or decrease brush diameter |
| `U` | Undo | Undo the previous editing operation |
| `Y` | Redo | Restore an undone operation |
| `X` | Reset | Restore the original image |
| `C` | Cancel | Cancel the current selection |
| `V` | Pixel Values | Print unique pixel values and counts |
| `S` | Save | Save the cleaned mask |
| `Q` | Quit | Close the editor |

### Method A: Keep a Rectangular Region

1. Press `R`.
2. Click and drag the mouse around the region you want to preserve.
3. A green rectangle appears while selecting.
4. Release the mouse button.
5. All pixels outside the selected rectangle become black.

### Method B: Erase a Rectangular Region

1. Press `E`.
2. Draw a rectangle over unwanted noise.
3. Release the mouse button.
4. All pixels inside the rectangle become black.

### Method C: Keep a Polygon Region

1. Press `P`.
2. Click several points around the object you want to preserve.
3. Press `Enter` to apply the polygon.
4. Pixels outside the polygon become black.

Use this method when the object has an irregular shape.

### Method D: Remove Noise Using a Brush

1. Press `B`.
2. Move the mouse over unwanted pixels.
3. Hold the left mouse button and drag to erase them.
4. Use `+` or `-` to adjust the brush size.

If you accidentally remove important pixels, press `U` to undo.

## 6. Example Workflow

Use the provided example image:

`4041_Control_C2_Day7_002.png`

**Recommended steps:**

1. Run the program in PyCharm.
2. Select the example PNG image.
3. Press `R` or `P` to preserve the main plant region.
4. Press `E` to remove larger unwanted regions.
5. Press `B` to manually remove small noise regions.
6. Press `V` to inspect unique pixel values.
7. Press `S` to save the cleaned mask.
8. Press `Q` to close the program.

The saved file will appear in:

```text
Interactive-Mask-Cleaner/
│
├── interactive_mask_cleaner.py
├── 4041_Control_C2_Day7_002.png
├── README.md
│
└── Cleaned/
    └── 4041_Control_C2_Day7_002.png
```

The original input image remains unchanged.

## 7. Unique Pixel Value Analysis

Press `V` to display unique pixel values and their counts in the PyCharm Run console.

Example output (illustrative):

```text
================================
UNIQUE PIXEL VALUES
================================
Total unique values: 3

Pixel Value | Count
          0 | 1850000
        128 | 120000
        255 | 430000
================================
```

This helps verify whether unwanted mask values remain after cleaning.

For images with identical RGB channels, the program reports the grayscale values. For other multichannel images, it reports unique pixel colors.

## 8. Saving the Cleaned Mask

Press `S` to save the edited mask.

The program:

- Automatically creates the output folder if necessary.
- Preserves the original filename.
- Maintains the original image width and height.
- Preserves unchanged pixel values in unedited regions.
- Saves the edited mask without including the green selection outlines or interface instructions.

**Note:** If a file with the same name already exists in the output folder, saving again will overwrite that file.

The displayed image may be scaled to fit the screen, but the saved image retains its original dimensions.

## 9. Troubleshooting

**Problem: `ModuleNotFoundError: No module named 'cv2'`**

Install OpenCV in the Python environment used by PyCharm:

```bash
pip install opencv-python
```

**Problem: Keyboard shortcuts are not working**

Click inside the OpenCV image window before pressing `R`, `E`, `B`, `S`, or other keys.

**Problem: The image selection window does not appear**

Check that Python includes Tkinter and that the program is running in a desktop environment.

**Problem: The output folder is missing**

Press `S` to save the edited image. Check the `OUTPUT_FOLDER` setting in the Python script.

**Problem: The image appears smaller than the original**

The editor scales large images for display. The saved mask retains its original dimensions.

## 10. Applications

This tool can be used for:

- Plant image segmentation mask refinement
- Agricultural image analysis
- Manual removal of segmentation artifacts
- Computer vision dataset preparation
- Image annotation quality control
- Medical and scientific image segmentation workflows

## 11. Contributing

Contributions, suggestions, and bug reports are welcome. You can open an issue or submit a pull request through GitHub.

## 12. License

Please refer to the repository's `LICENSE` file, if provided, for usage and distribution terms.
