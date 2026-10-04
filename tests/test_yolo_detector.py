from pathlib import Path

from src.preprocessing.yolo_detector import detect_qr


image_path = Path("data/tampered/tampered_01.png")

box = detect_qr(image_path)

print("\nYOLO DETECTION TEST")
print("-" * 30)

if box is None:
    print("No QR detected.")
else:
    print("QR detected!")
    print("Bounding box:", box)