import cv2
import numpy as np
from pathlib import Path

from src.preprocessing.yolo_detector import detect_qr
from src.forensics.refine_qr import refine_qr_bbox


def analyze_quiet_zone(image_path):
    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(f"Could not open: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 1: Detect QR using YOLO
    yolo_bbox = detect_qr(image_path)

    if yolo_bbox is None:
        print("QR code could not be detected by YOLO.")
        return None, None

    # Step 2: Refine the actual QR boundary
    bbox = refine_qr_bbox(image, yolo_bbox)

    if bbox is None:
        print("QR boundary could not be refined.")
        return None, None

    x1, y1, x2, y2 = bbox

    # Width of the quiet-zone area we inspect
    margin = 21

    height, width = gray.shape

    # Make four separate strips around the QR
    left_x1 = max(0, x1 - margin)
    left_x2 = x1

    right_x1 = x2
    right_x2 = min(width, x2 + margin)

    top_y1 = max(0, y1 - margin)
    top_y2 = y1

    bottom_y1 = y2
    bottom_y2 = min(height, y2 + margin)

    # Extract the four sides
    left = gray[y1:y2, left_x1:left_x2]
    right = gray[y1:y2, right_x1:right_x2]
    top = gray[top_y1:top_y2, x1:x2]
    bottom = gray[bottom_y1:bottom_y2, x1:x2]

    def dark_percentage(region):
        if region.size == 0:
            return 0.0

        dark_pixels = np.sum(region < 180)
        total_pixels = region.size

        return (dark_pixels / total_pixels) * 100

    left_score = dark_percentage(left)
    right_score = dark_percentage(right)
    top_score = dark_percentage(top)
    bottom_score = dark_percentage(bottom)

    # Find the most suspicious side
    side_scores = {
        "left": left_score,
        "right": right_score,
        "top": top_score,
        "bottom": bottom_score
    }

    suspicious_side = max(side_scores, key=side_scores.get)
    highest_percentage = side_scores[suspicious_side]

    # Prototype scoring
# We look for a side that is significantly different
# from the other three sides.

    values = list(side_scores.values())
    sorted_values = sorted(values)

    highest = sorted_values[-1]
    second_highest = sorted_values[-2]

    side_difference = highest - second_highest

    # Require a meaningful absolute dark-pixel concentration
    # before treating a side as a possible intrusion.
    if highest < 4.0:
        score = 0
    elif side_difference < 1.0:
        score = 5
    elif side_difference < 2.0:
        score = 10
    elif side_difference < 3.0:
        score = 20
    elif side_difference < 4.0:
        score = 30
    else:
        score = 35

    return {
        "left": left_score,
        "right": right_score,
        "top": top_score,
        "bottom": bottom_score,
        "suspicious_side": suspicious_side,
        "score": score,
        "bbox": bbox
    }, score


def test_image(image_path):
    print("\nAnalyzing:", image_path)

    result, score = analyze_quiet_zone(image_path)

    if result is None:
        return

    print(f"Left:   {result['left']:.2f}% dark")
    print(f"Right:  {result['right']:.2f}% dark")
    print(f"Top:    {result['top']:.2f}% dark")
    print(f"Bottom: {result['bottom']:.2f}% dark")

    print(f"Most suspicious side: {result['suspicious_side']}")
    print(f"Quiet-zone score: {score:.2f} / 35")

    if score > 5:
        print("Result: POSSIBLE QUIET-ZONE VIOLATION")
    else:
        print("Result: QUIET ZONE APPEARS CLEAN")


if __name__ == "__main__":
    genuine = Path("data/genuine/genuine_01.png")
    tampered = Path("data/tampered/tampered_01.png")

    test_image(genuine)
    test_image(tampered)