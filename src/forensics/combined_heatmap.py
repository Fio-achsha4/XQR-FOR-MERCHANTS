import cv2
import numpy as np
from pathlib import Path


def create_combined_heatmap(image_path):

    image_path = Path(image_path)

    image = cv2.imread(str(image_path))

    if image is None:
        print("Could not read image.")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # -----------------------------------------
    # Detect QR code
    # -----------------------------------------

    detector = cv2.QRCodeDetector()

    success, points = detector.detect(image)

    if not success or points is None:
        print("QR code could not be detected.")
        return

    points = points[0].astype(np.int32)

    # -----------------------------------------
    # Create QR mask
    # -----------------------------------------

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
    # Create forensic margin
    # -----------------------------------------

    inner_kernel = np.ones(
        (15, 15),
        np.uint8
    )

    outer_kernel = np.ones(
        (45, 45),
        np.uint8
    )

    inner = cv2.dilate(
        qr_mask,
        inner_kernel
    )

    outer = cv2.dilate(
        qr_mask,
        outer_kernel
    )

    margin = cv2.subtract(
        outer,
        inner
    )

    margin_pixels = margin > 0

    # -----------------------------------------
    # 1. Noise Variance signal
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

    variance = (
        local_squared_mean
        - local_mean ** 2
    )

    variance = np.maximum(
        variance,
        0
    )

    # -----------------------------------------
    # 2. ELA signal
    # -----------------------------------------

    # Save temporary JPEG
    temp_path = Path(
        "results/ela_temp.jpg"
    )

    temp_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(
        str(temp_path),
        image,
        [cv2.IMWRITE_JPEG_QUALITY, 90]
    )

    compressed = cv2.imread(
        str(temp_path)
    )

    compressed_gray = cv2.cvtColor(
        compressed,
        cv2.COLOR_BGR2GRAY
    )

    ela = cv2.absdiff(
        gray,
        compressed_gray
    )

    ela = ela.astype(
        np.float32
    )

    # -----------------------------------------
    # Normalize both signals
    # -----------------------------------------

    variance_signal = np.zeros_like(
        variance,
        dtype=np.float32
    )

    ela_signal = np.zeros_like(
        ela,
        dtype=np.float32
    )

    variance_signal[margin_pixels] = (
        variance[margin_pixels]
    )

    ela_signal[margin_pixels] = (
        ela[margin_pixels]
    )

    # Normalize each signal separately
    if np.max(variance_signal) > 0:

        variance_signal = cv2.normalize(
            variance_signal,
            None,
            0,
            1,
            cv2.NORM_MINMAX
        )

    if np.max(ela_signal) > 0:

        ela_signal = cv2.normalize(
            ela_signal,
            None,
            0,
            1,
            cv2.NORM_MINMAX
        )

    # -----------------------------------------
    # 3. Quiet-Zone signal
    # -----------------------------------------

    dark_pixels = (
        gray < 180
    ).astype(
        np.float32
    )

    quiet_signal = np.zeros_like(
        dark_pixels,
        dtype=np.float32
    )

    quiet_signal[margin_pixels] = (
        dark_pixels[margin_pixels]
    )

    # -----------------------------------------
    # Combine the 3 signals
    # -----------------------------------------

    combined = (
        0.40 * variance_signal
        + 0.35 * quiet_signal
        + 0.25 * ela_signal
    )

    # Keep only forensic margin
    combined[~margin_pixels] = 0

    # -----------------------------------------
    # Convert to heatmap
    # -----------------------------------------

    combined = cv2.normalize(
        combined,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    combined = combined.astype(
        np.uint8
    )

    heatmap = cv2.applyColorMap(
        combined,
        cv2.COLORMAP_JET
    )

    # -----------------------------------------
    # Overlay heatmap on original
    # -----------------------------------------

    overlay = image.copy()

    mask = margin_pixels

    overlay[mask] = cv2.addWeighted(
        image[mask],
        0.45,
        heatmap[mask],
        0.55,
        0
    )

    # Draw QR boundary
    cv2.polylines(
        overlay,
        [points],
        True,
        (255, 255, 255),
        2
    )

    # -----------------------------------------
    # Save result
    # -----------------------------------------

    output_folder = Path(
        "results/heatmaps"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_folder
        / f"{image_path.stem}_combined_heatmap.png"
    )

    cv2.imwrite(
        str(output_path),
        overlay
    )

    print(
        "\nCombined forensic heatmap created!"
    )

    print(
        f"Saved at: {output_path}"
    )


if __name__ == "__main__":

    create_combined_heatmap(
        "data/tampered/tampered_01.png"
    )