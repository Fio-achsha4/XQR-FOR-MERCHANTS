import cv2
import numpy as np
from pathlib import Path

from src.preprocessing.yolo_detector import detect_qr
from src.forensics.margin import create_margin_mask


def visualize(image_path):

    image = cv2.imread(str(image_path))

    bbox = detect_qr(image_path)

    if bbox is None:
        print("No QR detected.")
        return

    x1, y1, x2, y2 = bbox

    # Create the same quiet-zone mask
    mask = create_margin_mask(
        image,
        bbox,
        inner_margin=0,
        outer_margin=21
    )

    # Find dark pixels inside the mask
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    dark_pixels = np.logical_and(
        mask > 0,
        gray < 180
    )

    # Create visualization
    result = image.copy()

    # Draw YOLO bounding box in green
    cv2.rectangle(
        result,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    # Mark detected dark pixels in red
    result[dark_pixels] = (0, 0, 255)

    # Save result
    output_folder = Path("results/heatmaps")
    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_folder /
        f"{Path(image_path).stem}_quiet_test.png"
    )

    cv2.imwrite(
        str(output_path),
        result
    )

    print("\nQuiet-Zone visualization")
    print("-" * 30)
    print("Image:", image_path)
    print("YOLO box:", bbox)
    print("Dark pixels detected:", np.sum(dark_pixels))
    print("Saved:", output_path)


if __name__ == "__main__":

    visualize(
        Path("data/genuine/genuine_01.png")
    )

    visualize(
        Path("data/tampered/tampered_01.png")
    )