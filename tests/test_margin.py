import cv2
from pathlib import Path

from src.preprocessing.yolo_detector import detect_qr
from src.forensics.margin import create_margin_mask


image_path = Path("data/tampered/tampered_01.png")

image = cv2.imread(str(image_path))

bbox = detect_qr(image_path)

print("\nMARGIN MASK TEST")
print("-" * 30)

if bbox is None:
    print("No QR detected.")
else:
    print("QR bounding box:", bbox)

    margin_mask = create_margin_mask(image, bbox)

    output_path = Path("results/margin_test.png")
    cv2.imwrite(str(output_path), margin_mask)

    print("Margin mask created!")
    print("Saved to:", output_path)