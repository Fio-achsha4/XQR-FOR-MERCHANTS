import cv2
import numpy as np
from pathlib import Path


def analyze_noise_variance(image_path):
    """
    Analyze local noise variance in a margin
    surrounding the QR code.

    Returns:
        mean_variance
        score out of 40
        heatmap
    """

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Could not open: {image_path}"
        )

    # Convert to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Detect QR code
    detector = cv2.QRCodeDetector()
    success, points = detector.detect(image)

    if not success or points is None:
        print("QR code could not be detected.")
        return None, None, None

    # QR corner points
    points = points[0].astype(np.int32)

    # Create mask for QR itself
    qr_mask = np.zeros(
        gray.shape,
        dtype=np.uint8
    )

    cv2.fillPoly(
        qr_mask,
        [points],
        255
    )

    # -----------------------------------------
    # Create surrounding analysis ring
    # -----------------------------------------

    # Inner region protects us from QR edges
    inner_kernel = np.ones(
        (15, 15),
        np.uint8
    )

    # Outer region defines the analysis area
    outer_kernel = np.ones(
        (45, 45),
        np.uint8
    )

    inner_region = cv2.dilate(
        qr_mask,
        inner_kernel
    )

    outer_region = cv2.dilate(
        qr_mask,
        outer_kernel
    )

    # Only analyze the ring between
    # inner and outer regions
    margin_mask = cv2.subtract(
        outer_region,
        inner_region
    )

    # -----------------------------------------
    # Calculate local variance
    # -----------------------------------------

    gray_float = gray.astype(
        np.float32
    )

    local_mean = cv2.blur(
        gray_float,
        (7, 7)
    )

    local_squared_mean = cv2.blur(
        gray_float ** 2,
        (7, 7)
    )

    # Variance = E(X²) - E(X)²
    variance = (
        local_squared_mean
        - local_mean ** 2
    )

    variance = np.maximum(
        variance,
        0
    )

    # Only examine our margin
    margin_pixels = margin_mask > 0

    if np.sum(margin_pixels) == 0:
        return 0, 0, None

    margin_variance = variance[
        margin_pixels
    ]

    mean_variance = float(
        np.mean(margin_variance)
    )

    # -----------------------------------------
    # Convert to XQR score
    # Maximum = 40
    # -----------------------------------------

    if mean_variance < 20:
        score = 0

    elif mean_variance < 50:
        score = 10

    elif mean_variance < 100:
        score = 20

    elif mean_variance < 150:
        score = 30

    else:
        score = 40

    # -----------------------------------------
    # Create heatmap
    # -----------------------------------------

    heatmap = np.zeros_like(
        gray,
        dtype=np.float32
    )

    heatmap[margin_pixels] = variance[
        margin_pixels
    ]

    if np.max(heatmap) > 0:
        heatmap = cv2.normalize(
            heatmap,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

    heatmap = heatmap.astype(
        np.uint8
    )

    heatmap = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    return (
        mean_variance,
        score,
        heatmap
    )


def test_image(image_path):

    print(
        "\nAnalyzing:",
        image_path
    )

    variance, score, heatmap = (
        analyze_noise_variance(
            image_path
        )
    )

    if variance is None:
        return

    print(
        f"Mean noise variance: "
        f"{variance:.2f}"
    )

    print(
        f"Noise variance score: "
        f"{score:.2f} / 40"
    )

    if score > 5:
        print(
            "Result: POSSIBLE ABNORMAL "
            "NOISE/TEXTURE"
        )
    else:
        print(
            "Result: NO STRONG ABNORMAL "
            "NOISE DETECTED"
        )

    # Save heatmap
    output_folder = Path(
        "results/heatmaps"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_name = (
        Path(image_path).stem
        + "_noise_heatmap.png"
    )

    output_path = (
        output_folder / output_name
    )

    cv2.imwrite(
        str(output_path),
        heatmap
    )

    print(
        f"Heatmap saved at: {output_path}"
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