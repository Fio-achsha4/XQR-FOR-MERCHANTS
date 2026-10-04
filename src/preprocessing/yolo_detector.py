from pathlib import Path
from ultralytics import YOLO


MODEL_PATH = Path("runs/detect/train/weights/best.pt")

model = YOLO(MODEL_PATH)


def detect_qr(image_path):
    """
    Detect the QR code using the trained YOLO model.

    Returns:
        (x1, y1, x2, y2) if a QR is detected.
        None if no QR is detected.
    """

    results = model.predict(
        source=str(image_path),
        conf=0.05,
        verbose=False
    )

    result = results[0]

    if result.boxes is None or len(result.boxes) == 0:
        return None

    # Take the highest-confidence detection
    best_index = result.boxes.conf.argmax().item()

    box = result.boxes.xyxy[best_index].tolist()

    x1, y1, x2, y2 = map(int, box)

    return x1, y1, x2, y2