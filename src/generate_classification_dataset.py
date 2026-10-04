import cv2
import numpy as np
import qrcode
import random
from pathlib import Path
import shutil


BASE_DIR = Path("dataset_classification")

TRAIN_COUNT = 80
VAL_COUNT = 20

IMAGE_SIZE = 640

# Original XQR examples
ORIGINAL_GENUINE = Path("data/genuine/genuine_01.png")
ORIGINAL_TAMPERED = Path("data/tampered/tampered_01.png")

# Number of augmented copies of each original image
ORIGINAL_AUGMENTATIONS = 10


def create_qr():
    """Create a fresh QR code with different content."""

    merchant_id = random.randint(1000, 999999)

    qr_data = (
        f"upi://pay?"
        f"pa=merchant{merchant_id}@upi&"
        f"pn=DemoMerchant{merchant_id}&"
        f"am={random.randint(10, 999)}"
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")

    qr_image = np.array(qr_image)

    return cv2.cvtColor(qr_image, cv2.COLOR_RGB2BGR)


def create_scene(tampered=False):
    """Create synthetic QR scenes where tampering is the main class difference."""

    canvas = np.ones(
        (IMAGE_SIZE, IMAGE_SIZE, 3),
        dtype=np.uint8
    ) * random.randint(225, 255)

    qr = create_qr()

    qr_size = random.randint(260, 400)

    qr = cv2.resize(
        qr,
        (qr_size, qr_size),
        interpolation=cv2.INTER_NEAREST
    )

    angle = random.uniform(-8, 8)

    center = (
        qr_size // 2,
        qr_size // 2
    )

    matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    qr = cv2.warpAffine(
        qr,
        matrix,
        (qr_size, qr_size),
        borderValue=(255, 255, 255)
    )

    x = random.randint(
        80,
        IMAGE_SIZE - qr_size - 80
    )

    y = random.randint(
        80,
        IMAGE_SIZE - qr_size - 80
    )

    canvas[
        y:y + qr_size,
        x:x + qr_size
    ] = qr

    # ---------------------------------------------
    # ONLY tampered images receive the intrusion
    # ---------------------------------------------

    if tampered:

        intrusion = random.randint(10, 25)

        top_offset = random.randint(50, 90)
        bottom_offset = random.randint(50, 90)

        tamper_top = y + top_offset
        tamper_bottom = y + qr_size - bottom_offset

        dark_value = random.randint(30, 110)

        cv2.rectangle(
            canvas,
            (x - intrusion, tamper_top),
            (x + random.randint(2, 7), tamper_bottom),
            (dark_value,) * 3,
            -1
        )

        # Slightly irregular edges
        for _ in range(random.randint(2, 5)):

            px1 = x - random.randint(
                5,
                intrusion
            )

            py1 = random.randint(
                tamper_top,
                tamper_bottom
            )

            px2 = x + random.randint(1, 8)

            py2 = min(
                tamper_bottom,
                py1 + random.randint(5, 20)
            )

            cv2.rectangle(
                canvas,
                (px1, py1),
                (px2, py2),
                (random.randint(20, 120),) * 3,
                -1
            )

    # ---------------------------------------------
    # SAME camera conditions for BOTH classes
    # ---------------------------------------------

    noise = np.random.normal(
        0,
        random.uniform(1, 3),
        canvas.shape
    )

    canvas = np.clip(
        canvas.astype(np.float32) + noise,
        0,
        255
    ).astype(np.uint8)

    canvas = cv2.convertScaleAbs(
        canvas,
        alpha=random.uniform(0.95, 1.05),
        beta=random.randint(-10, 10)
    )

    return canvas

    if tampered:

        # XQR-style tampering:
# fraudulent sticker intrusion into the LEFT quiet-zone margin

        intrusion = random.randint(10, 25)

        top_offset = random.randint(50, 90)
        bottom_offset = random.randint(50, 90)

        tamper_top = y + top_offset
        tamper_bottom = y + qr_size - bottom_offset

        dark_value = random.randint(30, 110)

        # Main intrusion
        cv2.rectangle(
            canvas,
            (x - intrusion, tamper_top),
            (x + random.randint(2, 7), tamper_bottom),
            (dark_value,) * 3,
            -1
        )

        # Add a few irregular edges so the model doesn't
        # simply memorize a perfect rectangle.
        for _ in range(random.randint(2, 5)):

            px1 = x - random.randint(5, intrusion)
            py1 = random.randint(
                tamper_top,
                tamper_bottom
            )

            px2 = x + random.randint(1, 8)
            py2 = min(
                tamper_bottom,
                py1 + random.randint(5, 20)
            )

            cv2.rectangle(
                canvas,
                (px1, py1),
                (px2, py2),
                (random.randint(20, 120),) * 3,
                -1
            )

        # Add stronger print/background noise
        noise = np.random.normal(
            0,
            random.uniform(3, 8),
            canvas.shape
        )

        canvas = np.clip(
            canvas.astype(np.float32) + noise,
            0,
            255
        ).astype(np.uint8)

        # Slight contrast/brightness variation
        canvas = cv2.convertScaleAbs(
            canvas,
            alpha=random.uniform(0.95, 1.05),
            beta=random.randint(-10, 10)
        )

    else:

        # Genuine QR: only mild camera/printing noise
        noise = np.random.normal(
            0,
            random.uniform(1, 3),
            canvas.shape
        )

        canvas = np.clip(
            canvas.astype(np.float32) + noise,
            0,
            255
        ).astype(np.uint8)

    return canvas
def generate_images(split, count, class_name, tampered):

    output_dir = (
        BASE_DIR /
        split /
        class_name
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for i in range(count):

        image = create_scene(
            tampered=tampered
        )

        output_path = (
            output_dir /
            f"{class_name}_{i + 1:03d}.jpg"
        )

        cv2.imwrite(
            str(output_path),
            image
        )

    print(
        f"Created {count} independent "
        f"{class_name} images in {output_dir}"
    )


def augment_original(image_path, output_dir, class_name):

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Could not read: {image_path}"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for i in range(ORIGINAL_AUGMENTATIONS):

        augmented = image.copy()

        # Small rotation
        angle = random.uniform(-5, 5)

        height, width = augmented.shape[:2]

        center = (
            width // 2,
            height // 2
        )

        matrix = cv2.getRotationMatrix2D(
            center,
            angle,
            random.uniform(0.95, 1.05)
        )

        augmented = cv2.warpAffine(
            augmented,
            matrix,
            (width, height),
            borderMode=cv2.BORDER_REFLECT
        )

        # Small brightness variation
        brightness = random.randint(-15, 15)

        augmented = cv2.convertScaleAbs(
            augmented,
            alpha=random.uniform(0.95, 1.05),
            beta=brightness
        )

        # Mild camera noise
        noise = np.random.normal(
            0,
            random.uniform(0.5, 2.0),
            augmented.shape
        )

        augmented = np.clip(
            augmented.astype(np.float32) + noise,
            0,
            255
        ).astype(np.uint8)

        output_path = (
            output_dir /
            f"original_{class_name}_{i + 1:02d}.jpg"
        )

        cv2.imwrite(
            str(output_path),
            augmented
        )

    print(
        f"Added {ORIGINAL_AUGMENTATIONS} augmented "
        f"copies of original {class_name} image."
    )


def main():

    # Recreate dataset from scratch
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)

    # Independent synthetic training images
    generate_images(
        "train",
        TRAIN_COUNT,
        "genuine",
        False
    )

    generate_images(
        "train",
        TRAIN_COUNT,
        "tampered",
        True
    )

    # Independent synthetic validation images
    generate_images(
        "val",
        VAL_COUNT,
        "genuine",
        False
    )

    generate_images(
        "val",
        VAL_COUNT,
        "tampered",
        True
    )

    # Add original XQR examples ONLY to training
    augment_original(
        ORIGINAL_GENUINE,
        BASE_DIR / "train" / "genuine",
        "genuine"
    )

    augment_original(
        ORIGINAL_TAMPERED,
        BASE_DIR / "train" / "tampered",
        "tampered"
    )

    print("\nClassification dataset created.")
    print("Independent validation set preserved.")
    print("Original XQR examples added only to training.")


if __name__ == "__main__":
    main()