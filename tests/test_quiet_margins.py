import cv2
import numpy as np
from pathlib import Path

from src.preprocessing.yolo_detector import detect_qr
from src.forensics.refine_qr import refine_qr_bbox
from src.forensics.margin import create_margin_mask


def test_image(image_path):

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

    print("\nImage:", image_path)
    print("Refined QR box:", bbox)

    for outer_margin in [10, 15, 21, 30, 45, 60]:

        mask = create_margin_mask(
            image,
            bbox,
            inner_margin=0,
            outer_margin=outer_margin
        )

        dark_pixels = np.logical_and(
            mask > 0,
            gray < 180
        )

        total_pixels = np.sum(mask > 0)
        dark_count = np.sum(dark_pixels)

        if total_pixels == 0:
            percentage = 0
        else:
            percentage = (
                dark_count / total_pixels
            ) * 100

        print(
            f"Margin {outer_margin:>2}px:"
            f" {percentage:.2f}% dark"
        )


if __name__ == "__main__":

    test_image(
        Path("data/genuine/genuine_01.png")
    )

    test_image(
        Path("data/tampered/tampered_01.png")
    )