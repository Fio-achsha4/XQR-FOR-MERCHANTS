import cv2
from pathlib import Path

from src.preprocessing.yolo_detector import detect_qr
from src.forensics.refine_qr import refine_qr_bbox


def test_image(image_path):

    image = cv2.imread(str(image_path))

    yolo_bbox = detect_qr(image_path)

    print("\nImage:", image_path)
    print("YOLO box:", yolo_bbox)

    if yolo_bbox is None:
        print("YOLO could not detect QR.")
        return

    refined_bbox = refine_qr_bbox(
        image,
        yolo_bbox
    )

    print("Refined box:", refined_bbox)


if __name__ == "__main__":

    test_image(
        Path("data/genuine/genuine_01.png")
    )

    test_image(
        Path("data/tampered/tampered_01.png")
    )