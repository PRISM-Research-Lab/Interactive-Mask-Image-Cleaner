
"""
Interactive Mask Cleaner with File Selection

Install:
    pip install opencv-python numpy

Controls:
R = Keep Rectangle (outside becomes black)
E = Erase Rectangle (inside becomes black)
P = Keep Polygon (outside becomes black)
B = Black Brush
U = Undo
Y = Redo
X = Reset Original
C = Cancel Selection
+/- = Brush Size
V = Show Unique Pixel Values
S = Save
Q = Quit
"""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np


# ============================================================
# USER SETTINGS
# ============================================================

# Output folder (automatically created if missing)
OUTPUT_FOLDER = r"C:\WVSU_Documents\Research\Scripts\Test_projectV1\Cleaned"

MAX_WIDTH = 1200
MAX_HEIGHT = 850

INITIAL_BRUSH_SIZE = 24
MAX_UNDO = 20

# True: erased BGRA pixels become (0, 0, 0, 255)
# False: erased BGRA pixels become (0, 0, 0, 0)
OPAQUE_BLACK = True


# ============================================================
# SELECT INPUT IMAGE
# ============================================================

def select_input_image():

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    image_path = filedialog.askopenfilename(
        parent=root,
        title="Select Mask Image",
        filetypes=[
            ("PNG Images", "*.png"),
            ("TIFF Images", "*.tif *.tiff"),
            ("JPEG Images", "*.jpg *.jpeg"),
            (
                "All Image Files",
                "*.png *.jpg *.jpeg *.tif *.tiff *.bmp"
            ),
            ("All Files", "*.*")
        ]
    )

    root.destroy()
    return image_path


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. Select input image
    # --------------------------------------------------------

    selected_image = select_input_image()

    if not selected_image:
        print("No image selected. Program closed.")
        return

    source = Path(selected_image)

    if not source.is_file():
        raise FileNotFoundError(
            f"Image not found: {source}"
        )

    original = cv2.imread(
        str(source),
        cv2.IMREAD_UNCHANGED
    )

    if original is None:
        raise ValueError("Could not read selected image.")

    current = original.copy()
    h, w = current.shape[:2]

    # --------------------------------------------------------
    # 2. Create output folder
    # --------------------------------------------------------

    output_dir = Path(OUTPUT_FOLDER)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nImage loaded:", source.name)
    print("Original dimensions:", w, "x", h)
    print("Original shape:", original.shape)
    print("Data type:", original.dtype)
    print("Output folder:", output_dir.resolve())

    # --------------------------------------------------------
    # 3. Display scaling
    # --------------------------------------------------------

    scale = min(
        1.0,
        MAX_WIDTH / w,
        MAX_HEIGHT / h
    )

    display_w = max(1, round(w * scale))
    display_h = max(1, round(h * scale))

    window = "Interactive Mask Cleaner"

    # --------------------------------------------------------
    # 4. Editor state
    # --------------------------------------------------------

    mode = "brush"
    brush = INITIAL_BRUSH_SIZE

    polygon = []
    start = None
    current_mouse = None
    dragging = False
    last = None

    undo_stack = []
    redo_stack = []

    # --------------------------------------------------------
    # 5. Undo / Redo
    # --------------------------------------------------------

    def snapshot():

        undo_stack.append(current.copy())

        if len(undo_stack) > MAX_UNDO:
            undo_stack.pop(0)

        redo_stack.clear()

    def undo():

        nonlocal current, dragging, start, last

        if undo_stack:

            redo_stack.append(current.copy())
            current = undo_stack.pop()

            polygon.clear()
            dragging = False
            start = None
            last = None

            print("Undo completed.")

        else:
            print("Nothing to undo.")

    def redo():

        nonlocal current, dragging, start, last

        if redo_stack:

            undo_stack.append(current.copy())

            if len(undo_stack) > MAX_UNDO:
                undo_stack.pop(0)

            current = redo_stack.pop()

            polygon.clear()
            dragging = False
            start = None
            last = None

            print("Redo completed.")

        else:
            print("Nothing to redo.")

    # --------------------------------------------------------
    # 6. Black pixel value
    # --------------------------------------------------------

    def black_value():

        if current.ndim == 2:
            return 0

        channels = current.shape[2]

        if channels == 4 and OPAQUE_BLACK:
            return (
                0, 0, 0,
                np.iinfo(current.dtype).max
            )

        return tuple([0] * channels)

    # --------------------------------------------------------
    # 7. Coordinates
    # --------------------------------------------------------

    def coords(x, y):

        px = min(
            w - 1,
            max(0, round(x / scale))
        )

        py = min(
            h - 1,
            max(0, round(y / scale))
        )

        return px, py

    def display_coords(p):

        return (
            round(p[0] * scale),
            round(p[1] * scale)
        )

    # --------------------------------------------------------
    # 8. Black brush
    # --------------------------------------------------------

    def draw_line(p, q):

        cv2.line(
            current,
            p,
            q,
            black_value(),
            thickness=brush,
            lineType=cv2.LINE_8
        )

        cv2.circle(
            current,
            q,
            max(1, brush // 2),
            black_value(),
            -1,
            lineType=cv2.LINE_8
        )

    # --------------------------------------------------------
    # 9. Keep ROI
    # --------------------------------------------------------

    def keep_mask(roi):

        snapshot()

        # Pixels outside selected region become black.
        current[roi == 0] = black_value()

        print("Keep ROI applied. Outside is black.")

    # --------------------------------------------------------
    # 10. Erase Rectangle
    # --------------------------------------------------------

    def erase_rectangle(p1, p2):

        x0, x1 = sorted((p1[0], p2[0]))
        y0, y1 = sorted((p1[1], p2[1]))

        if x1 <= x0 or y1 <= y0:
            return

        snapshot()

        current[y0:y1 + 1, x0:x1 + 1] = black_value()

        print("Rectangle erased. Inside is black.")

    # --------------------------------------------------------
    # 11. Mouse callback
    # --------------------------------------------------------

    def mouse(event, x, y, flags, userdata):

        nonlocal dragging, start, last, current_mouse

        p = coords(x, y)
        current_mouse = p

        # BLACK BRUSH
        if mode == "brush":

            if event == cv2.EVENT_LBUTTONDOWN:

                snapshot()
                dragging = True
                last = p
                draw_line(p, p)

            elif event == cv2.EVENT_MOUSEMOVE and dragging:

                draw_line(last, p)
                last = p

            elif event == cv2.EVENT_LBUTTONUP:

                if dragging and last is not None:
                    draw_line(last, p)

                dragging = False
                last = None

        # RECTANGLE MODES
        elif mode in ("keep_rectangle", "erase_rectangle"):

            if event == cv2.EVENT_LBUTTONDOWN:

                start = p
                dragging = True

            elif event == cv2.EVENT_MOUSEMOVE and dragging:

                current_mouse = p

            elif event == cv2.EVENT_LBUTTONUP and dragging:

                x0, x1 = sorted((start[0], p[0]))
                y0, y1 = sorted((start[1], p[1]))

                if x1 > x0 and y1 > y0:

                    if mode == "keep_rectangle":

                        roi = np.zeros(
                            (h, w),
                            np.uint8
                        )

                        cv2.rectangle(
                            roi,
                            (x0, y0),
                            (x1, y1),
                            255,
                            -1
                        )

                        keep_mask(roi)

                    else:

                        erase_rectangle(start, p)

                start = None
                dragging = False

        # POLYGON MODE
        elif mode == "polygon":

            if event == cv2.EVENT_LBUTTONDOWN:

                polygon.append(p)
                print("Polygon point:", p)

    # --------------------------------------------------------
    # 12. Unique pixel values
    # --------------------------------------------------------

    def show_unique():

        if current.ndim == 2:

            plane = current

        elif (
            current.shape[2] >= 3
            and np.array_equal(
                current[..., 0],
                current[..., 1]
            )
            and np.array_equal(
                current[..., 1],
                current[..., 2]
            )
        ):

            plane = current[..., 0]

        else:

            pixels = current.reshape(
                -1,
                current.shape[2]
            )

            values, counts = np.unique(
                pixels,
                axis=0,
                return_counts=True
            )

            print("\nUnique pixel colors:", len(values))

            for value, count in zip(values, counts):
                print(tuple(map(int, value)), int(count))

            return

        values, counts = np.unique(
            plane,
            return_counts=True
        )

        print("\n================================")
        print("UNIQUE PIXEL VALUES")
        print("================================")
        print("Total unique values:", len(values))
        print("Pixel Value | Count")

        for value, count in zip(values, counts):

            print(
                f"{int(value):>11} | {int(count)}"
            )

        print("================================\n")

    # --------------------------------------------------------
    # 13. Render image and previews
    # --------------------------------------------------------

    def render():

        preview = current.copy()

        if preview.ndim == 2:

            preview = cv2.cvtColor(
                preview,
                cv2.COLOR_GRAY2BGR
            )

        elif preview.shape[2] == 4:

            preview = cv2.cvtColor(
                preview,
                cv2.COLOR_BGRA2BGR
            )

        preview = cv2.resize(
            preview,
            (display_w, display_h),
            interpolation=cv2.INTER_NEAREST
        )

        # GREEN RECTANGLE PREVIEW
        if (
            mode in ("keep_rectangle", "erase_rectangle")
            and dragging
            and start is not None
            and current_mouse is not None
        ):

            p1 = display_coords(start)
            p2 = display_coords(current_mouse)

            overlay = preview.copy()

            cv2.rectangle(
                overlay,
                p1,
                p2,
                (0, 255, 0),
                -1
            )

            preview = cv2.addWeighted(
                overlay,
                0.20,
                preview,
                0.80,
                0
            )

            cv2.rectangle(
                preview,
                p1,
                p2,
                (0, 255, 0),
                2
            )

        # GREEN POLYGON PREVIEW
        if mode == "polygon" and polygon:

            points = np.array(
                [
                    display_coords(p)
                    for p in polygon
                ],
                dtype=np.int32
            )

            cv2.polylines(
                preview,
                [points],
                False,
                (0, 255, 0),
                2
            )

            for pt in points:

                cv2.circle(
                    preview,
                    tuple(pt),
                    4,
                    (0, 255, 0),
                    -1
                )

            if current_mouse is not None:

                cv2.line(
                    preview,
                    tuple(points[-1]),
                    display_coords(current_mouse),
                    (0, 255, 0),
                    1
                )

        # BRUSH CURSOR
        if mode == "brush" and current_mouse is not None:

            center = display_coords(current_mouse)

            radius = max(
                1,
                round(brush * scale / 2)
            )

            cv2.circle(
                preview,
                center,
                radius,
                (0, 255, 0),
                1
            )

        # ----------------------------------------------------
        # PERMANENT INSTRUCTIONS
        # ----------------------------------------------------

        mode_names = {
            "brush": "BLACK BRUSH",
            "keep_rectangle": "KEEP RECTANGLE",
            "erase_rectangle": "ERASE RECTANGLE",
            "polygon": "KEEP POLYGON"
        }

        panel_height = 100

        overlay = preview.copy()

        cv2.rectangle(
            overlay,
            (0, 0),
            (
                display_w,
                min(panel_height, display_h)
            ),
            (25, 25, 25),
            -1
        )

        preview = cv2.addWeighted(
            overlay,
            0.85,
            preview,
            0.15,
            0
        )

        lines = [
            f"MODE: {mode_names[mode]} | BRUSH: {brush}px",
            "R:Keep Rect  E:Erase Rect  P:Polygon  B:Brush",
            "U:Undo  Y:Redo  X:Reset  C:Cancel  +/-:Brush",
            "ENTER:Apply Polygon  V:Pixels  S:SAVE  Q:QUIT"
        ]

        for i, text in enumerate(lines):

            color = (
                (0, 255, 255)
                if i == 0
                else (255, 255, 255)
            )

            if i == 3:
                color = (0, 255, 0)

            cv2.putText(
                preview,
                text,
                (8, 20 + i * 23),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                color,
                1,
                cv2.LINE_AA
            )

        return preview

    # --------------------------------------------------------
    # 14. Print controls
    # --------------------------------------------------------

    print("\n================================")
    print("INTERACTIVE MASK CLEANER")
    print("================================")
    print("R = Keep rectangle")
    print("E = Erase rectangle")
    print("P = Keep polygon")
    print("B = Black brush")
    print("ENTER = Apply polygon")
    print("U = Undo")
    print("Y = Redo")
    print("X = Reset")
    print("C = Cancel")
    print("+/- = Brush size")
    print("V = Unique pixel values")
    print("S = SAVE")
    print("Q = QUIT")
    print("================================\n")

    # --------------------------------------------------------
    # 15. Open window
    # --------------------------------------------------------

    cv2.namedWindow(
        window,
        cv2.WINDOW_AUTOSIZE
    )

    cv2.setMouseCallback(
        window,
        mouse
    )

    # --------------------------------------------------------
    # 16. Main loop
    # --------------------------------------------------------

    while True:

        cv2.imshow(window, render())

        key = cv2.waitKey(30) & 0xFF

        # Quit
        if key in (ord("q"), 27):
            break

        # Brush mode
        elif key == ord("b"):

            mode = "brush"
            dragging = False
            start = None
            last = None
            polygon.clear()

            print("Mode: Black Brush")

        # Keep rectangle
        elif key == ord("r"):

            mode = "keep_rectangle"
            dragging = False
            start = None
            polygon.clear()

            print("Mode: Keep Rectangle")

        # Erase rectangle
        elif key == ord("e"):

            mode = "erase_rectangle"
            dragging = False
            start = None
            polygon.clear()

            print("Mode: Erase Rectangle")

        # Polygon
        elif key == ord("p"):

            mode = "polygon"
            dragging = False
            start = None
            polygon.clear()

            print("Mode: Keep Polygon")

        # Increase brush
        elif key in (ord("+"), ord("=")):

            brush = min(500, brush + 5)
            print("Brush size:", brush)

        # Decrease brush
        elif key in (ord("-"), ord("_")):

            brush = max(1, brush - 5)
            print("Brush size:", brush)

        # Apply polygon
        elif key in (13, 10) and mode == "polygon":

            if len(polygon) >= 3:

                roi = np.zeros(
                    (h, w),
                    np.uint8
                )

                cv2.fillPoly(
                    roi,
                    [np.asarray(polygon, np.int32)],
                    255
                )

                keep_mask(roi)
                polygon.clear()

                print("Polygon applied.")

            else:
                print("Select at least 3 polygon points.")

        # Cancel selection
        elif key == ord("c"):

            polygon.clear()
            start = None
            dragging = False

            print("Selection cancelled.")

        # Undo
        elif key == ord("u"):
            undo()

        # Redo
        elif key == ord("y"):
            redo()

        # Reset
        elif key == ord("x"):

            snapshot()
            current = original.copy()

            polygon.clear()
            start = None
            dragging = False

            print("Reset to original.")

        # Unique pixels
        elif key == ord("v"):
            show_unique()

        # Save
        elif key == ord("s"):

            output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            destination = output_dir / source.name

            success = cv2.imwrite(
                str(destination),
                current
            )

            if success:

                print("\nIMAGE SAVED SUCCESSFULLY")
                print("Location:", destination.resolve())
                print("Saved dimensions:", w, "x", h)

                show_unique()

            else:
                print("ERROR saving:", destination)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
