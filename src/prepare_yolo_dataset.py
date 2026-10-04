import cv2
import shutil
from pathlib import Path


# -----------------------------------------
# Project paths
# -----------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_FOLDERS = [
    PROJECT_ROOT / "data" / "genuine",
    PROJECT_ROOT / "data" / "tampered",
]

TRAIN_IMAGES = PROJECT_ROOT / "dataset" / "images" / "train"
TRAIN_LABELS = PROJECT_ROOT / "dataset" / "labels" / "train"


# Create destination folders
TRAIN_IMAGES.mkdir(parents=True, exist_ok=True)
TRAIN_LABELS.mkdir(parents=True, exist_ok=True)


# -----------------------------------------
# Convert QR corners to YOLO format
# -----------------------------------------

def create_yolo_label(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read: {image_path}")
        return False

    height, width = image.shape[:2]

    detector = cv2.QRCodeDetector()

    success, points = detector.detect(image)

    if not success or points is None:
        print(f"QR not detected: {image_path.name}")
        return False

    points = points[0]

    # Bounding box
    x_min = points[:, 0].min()
    y_min = points[:, 1].min()

    x_max = points[:, 0].max()
    y_max = points[:, 1].max()

    # YOLO format
    x_center = ((x_min + x_max) / 2) / width
    y_center = ((y_min + y_max) / 2) / height

    box_width = (x_max - x_min) / width
    box_height = (y_max - y_min) / height

    # Class 0 = QR code
    label = (
        f"0 "
        f"{x_center:.6f} "
        f"{y_center:.6f} "
        f"{box_width:.6f} "
        f"{box_height:.6f}"
    )

    label_path = (
        TRAIN_LABELS /
        f"{image_path.stem}.txt"
    )

    label_path.write_text(
        label + "\n",
        encoding="utf-8"
    )

    return True


# -----------------------------------------
# Process images
# -----------------------------------------

for folder in SOURCE_FOLDERS:

    for image_path in folder.glob("*.png"):

        print(f"\nProcessing: {image_path.name}")

        if create_yolo_label(image_path):

            destination = (
                TRAIN_IMAGES /
                image_path.name
            )

            shutil.copy2(
                image_path,
                destination
            )

            print("✓ Image copied")
            print("✓ YOLO label created")


print("\n" + "=" * 50)
print("YOLO DATASET PREPARATION COMPLETE")
print("=" * 50)