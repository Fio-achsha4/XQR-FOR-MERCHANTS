import cv2
import numpy as np
from pathlib import Path
from PIL import Image

from src.preprocessing.yolo_detector import detect_qr
from src.forensics.margin import create_margin_mask


def analyze_ela(image_path):
    """
    Perform Error Level Analysis (ELA).

    The image is temporarily saved as JPEG and compared
    with the original. Analysis is restricted to the
    margin surrounding the QR code.

    Returns:
        mean_ela
        score out of 25
        ela_map
    """

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Could not open: {image_path}"
        )

    # -----------------------------------------
    # Detect QR using YOLO
    # -----------------------------------------

    bbox = detect_qr(image_path)

    if bbox is None:
        print("QR code could not be detected by YOLO.")
        return None, None, None

    # -----------------------------------------
    # Create analysis margin using YOLO box
    # -----------------------------------------

    margin_mask = create_margin_mask(
        image,
        bbox,
        inner_margin=15,
        outer_margin=45
    )
    # -----------------------------------------
    # Error Level Analysis
    # -----------------------------------------

    original = Image.open(
        image_path
    ).convert("RGB")

    temporary_file = Path(
        "results/ela_temp.jpg"
    )

    temporary_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Re-save at JPEG quality 90
    original.save(
        temporary_file,
        "JPEG",
        quality=90
    )

    recompressed = cv2.imread(
        str(temporary_file)
    )

    original_cv = cv2.cvtColor(
        np.array(original),
        cv2.COLOR_RGB2BGR
    )

    # Make sure dimensions match
    recompressed = cv2.resize(
        recompressed,
        (
            original_cv.shape[1],
            original_cv.shape[0]
        )
    )

    # Absolute pixel difference
    difference = cv2.absdiff(
        original_cv,
        recompressed
    )

    # Convert difference to grayscale
    ela_gray = cv2.cvtColor(
        difference,
        cv2.COLOR_BGR2GRAY
    )

    # -----------------------------------------
    # Measure only the margin
    # -----------------------------------------

    margin_pixels = margin_mask > 0

    if np.sum(margin_pixels) == 0:
        return 0, 0, None

    ela_values = ela_gray[
        margin_pixels
    ]

    mean_ela = float(
        np.mean(ela_values)
    )

    # -----------------------------------------
    # Convert ELA to score
    # Maximum = 25
    # -----------------------------------------

    if mean_ela < 2:
        score = 0

    elif mean_ela < 5:
        score = 5

    elif mean_ela < 10:
        score = 10

    elif mean_ela < 20:
        score = 15

    elif mean_ela < 30:
        score = 20

    else:
        score = 25

    # -----------------------------------------
    # Create ELA map
    # -----------------------------------------

    ela_map = np.zeros_like(
        ela_gray
    )

    ela_map[margin_pixels] = (
        ela_gray[margin_pixels]
    )

    if np.max(ela_map) > 0:
        ela_map = cv2.normalize(
            ela_map,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

    ela_map = ela_map.astype(
        np.uint8
    )

    ela_map = cv2.applyColorMap(
        ela_map,
        cv2.COLORMAP_JET
    )

    return (
        mean_ela,
        score,
        ela_map
    )


def test_image(image_path):

    print(
        "\nAnalyzing:",
        image_path
    )

    mean_ela, score, ela_map = (
        analyze_ela(image_path)
    )

    if mean_ela is None:
        return

    print(
        f"Mean ELA value: "
        f"{mean_ela:.2f}"
    )

    print(
        f"ELA score: "
        f"{score:.2f} / 25"
    )

    if score > 5:
        print(
            "Result: POSSIBLE "
            "COMPRESSION/EDITING DIFFERENCE"
        )
    else:
        print(
            "Result: NO STRONG ELA "
            "ANOMALY DETECTED"
        )

    # Save ELA map
    output_folder = Path(
        "results/heatmaps"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_name = (
        Path(image_path).stem
        + "_ela_map.png"
    )

    output_path = (
        output_folder / output_name
    )

    cv2.imwrite(
        str(output_path),
        ela_map
    )

    print(
        f"ELA map saved at: {output_path}"
    )


if __name__ == "__main__":

    genuine = Path(
        "data/genuine/genuine_01.png"
    )

    tampered = Path(
        "data/tampered/tampered_01.png"
    )

    test_image(genuine)
    test_image(tampered)