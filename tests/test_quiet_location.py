import cv2
import numpy as np
from pathlib import Path

from src.preprocessing.yolo_detector import detect_qr
from src.forensics.refine_qr import refine_qr_bbox
from src.forensics.margin import create_margin_mask


def analyze(image_path):

    image = cv2.imread(str(image_path))

    yolo_bbox = detect_qr(image_path)

    if yolo_bbox is None:
        print("YOLO detection failed.")
        return

    bbox = refine_qr_bbox(
        image,
        yolo_bbox
    )

    if bbox is None:
        print("QR refinement failed.")
        return

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    mask = create_margin_mask(
        image,
        bbox,
        inner_margin=0,
        outer_margin=21
    )

    dark = np.logical_and(
        mask > 0,
        gray < 180
    )

    ys, xs = np.where(dark)

    print("\nImage:", image_path)
    print("QR box:", bbox)

    if len(xs) == 0:
        print("No dark pixels found in margin.")
        return

    print("Dark pixels:", len(xs))
    print("Dark pixel location:")
    print(
        f"  X: {xs.min()} to {xs.max()}"
    )
    print(
        f"  Y: {ys.min()} to {ys.max()}"
    )

    x1, y1, x2, y2 = bbox

    # Determine which side contains the most dark pixels
    left = np.sum(xs < x1)
    right = np.sum(xs >= x2)
    top = np.sum(ys < y1)
    bottom = np.sum(ys >= y2)

    print("Dark pixels by side:")
    print("  Left  :", left)
    print("  Right :", right)
    print("  Top   :", top)
    print("  Bottom:", bottom)


if __name__ == "__main__":

    analyze(
        Path("data/genuine/genuine_01.png")
    )

    analyze(
        Path("data/tampered/tampered_01.png")
    )