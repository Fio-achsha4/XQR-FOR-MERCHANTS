import random
import shutil
from pathlib import Path

import cv2
import numpy as np
import qrcode
from PIL import Image, ImageEnhance


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TRAIN_IMAGES = PROJECT_ROOT / "dataset" / "images" / "train"
TRAIN_LABELS = PROJECT_ROOT / "dataset" / "labels" / "train"

VAL_IMAGES = PROJECT_ROOT / "dataset" / "images" / "val"
VAL_LABELS = PROJECT_ROOT / "dataset" / "labels" / "val"


# ============================================================
# SETTINGS
# ============================================================

TRAIN_COUNT = 80
VAL_COUNT = 20

IMAGE_SIZE = 640


# ============================================================
# CREATE FOLDERS
# ============================================================

for folder in [
    TRAIN_IMAGES,
    TRAIN_LABELS,
    VAL_IMAGES,
    VAL_LABELS,
]:
    folder.mkdir(parents=True, exist_ok=True)


# ============================================================
# CREATE QR IMAGE
# ============================================================

def create_qr(index):

    # Fake/demo UPI-style information
    upi_id = f"demo{index}@xqr"

    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(
        f"upi://pay?pa={upi_id}&pn=XQR Demo Merchant"
    )

    qr.make(
        fit=True
    )

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")

    # Resize QR to random size
    qr_size = random.randint(
        260,
        430
    )

    qr_image = qr_image.resize(
        (qr_size, qr_size),
        Image.Resampling.NEAREST
    )

    # Random rotation
    angle = random.uniform(
        -8,
        8
    )

    qr_image = qr_image.rotate(
        angle,
        expand=True,
        fillcolor="white"
    )

    return qr_image


# ============================================================
# CREATE BACKGROUND
# ============================================================

def create_background():

    background = np.random.randint(
        180,
        256,
        (IMAGE_SIZE, IMAGE_SIZE, 3),
        dtype=np.uint8
    )

    # Smooth background
    background = cv2.GaussianBlur(
        background,
        (21, 21),
        0
    )

    return Image.fromarray(
        cv2.cvtColor(
            background,
            cv2.COLOR_BGR2RGB
        )
    )


# ============================================================
# CREATE ONE IMAGE
# ============================================================

def create_image(index):

    background = create_background()

    qr_image = create_qr(index)

    # Slight brightness variation
    brightness = random.uniform(
        0.85,
        1.15
    )

    qr_image = ImageEnhance.Brightness(
        qr_image
    ).enhance(brightness)

    # Slight contrast variation
    contrast = random.uniform(
        0.90,
        1.10
    )

    qr_image = ImageEnhance.Contrast(
        qr_image
    ).enhance(contrast)

    qr_width, qr_height = qr_image.size

    # Random position
    max_x = IMAGE_SIZE - qr_width
    max_y = IMAGE_SIZE - qr_height

    x = random.randint(
        20,
        max(20, max_x - 20)
    )

    y = random.randint(
        20,
        max(20, max_y - 20)
    )

    background.paste(
        qr_image,
        (x, y)
    )

    # Add slight camera-like noise
    image_array = np.array(
        background
    ).astype(
        np.float32
    )

    noise_strength = random.uniform(
        0,
        4
    )

    noise = np.random.normal(
        0,
        noise_strength,
        image_array.shape
    )

    image_array += noise

    image_array = np.clip(
        image_array,
        0,
        255
    ).astype(
        np.uint8
    )

    final_image = Image.fromarray(
        image_array
    )

    return final_image, x, y, qr_width, qr_height


# ============================================================
# CREATE YOLO LABEL
# ============================================================

def create_label(
    x,
    y,
    qr_width,
    qr_height
):

    x_center = (
        x + qr_width / 2
    ) / IMAGE_SIZE

    y_center = (
        y + qr_height / 2
    ) / IMAGE_SIZE

    width = (
        qr_width / IMAGE_SIZE
    )

    height = (
        qr_height / IMAGE_SIZE
    )

    # Class 0 = QR code
    return (
        f"0 "
        f"{x_center:.6f} "
        f"{y_center:.6f} "
        f"{width:.6f} "
        f"{height:.6f}\n"
    )


# ============================================================
# GENERATE DATASET
# ============================================================

def generate_dataset():

    print("=" * 55)
    print("       XQR YOLO DATASET GENERATOR")
    print("=" * 55)

    # ----------------------------------------
    # Training images
    # ----------------------------------------

    print("\nGenerating training images...")

    for i in range(
        TRAIN_COUNT
    ):

        image, x, y, w, h = create_image(
            i
        )

        filename = (
            f"qr_train_{i:03d}.jpg"
        )

        image_path = (
            TRAIN_IMAGES / filename
        )

        label_path = (
            TRAIN_LABELS
            / f"qr_train_{i:03d}.txt"
        )

        image.save(
            image_path,
            quality=95
        )

        label_path.write_text(
            create_label(
                x,
                y,
                w,
                h
            ),
            encoding="utf-8"
        )

        print(
            f"Train {i + 1}/{TRAIN_COUNT}",
            end="\r"
        )

    print(
        "\n✓ Training dataset created."
    )

    # ----------------------------------------
    # Validation images
    # ----------------------------------------

    print("\nGenerating validation images...")

    for i in range(
        VAL_COUNT
    ):

        image, x, y, w, h = create_image(
            TRAIN_COUNT + i
        )

        filename = (
            f"qr_val_{i:03d}.jpg"
        )

        image_path = (
            VAL_IMAGES / filename
        )

        label_path = (
            VAL_LABELS
            / f"qr_val_{i:03d}.txt"
        )

        image.save(
            image_path,
            quality=95
        )

        label_path.write_text(
            create_label(
                x,
                y,
                w,
                h
            ),
            encoding="utf-8"
        )

        print(
            f"Validation {i + 1}/{VAL_COUNT}",
            end="\r"
        )

    print(
        "\n✓ Validation dataset created."
    )

    print("\n" + "=" * 55)
    print("       DATASET GENERATION COMPLETE")
    print("=" * 55)

    print(
        f"\nTraining images:   {TRAIN_COUNT}"
    )

    print(
        f"Validation images: {VAL_COUNT}"
    )


if __name__ == "__main__":

    generate_dataset()