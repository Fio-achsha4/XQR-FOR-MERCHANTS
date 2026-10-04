import cv2
import numpy as np


def refine_qr_bbox(image, yolo_bbox, padding=30):
    """
    Refine the YOLO QR bounding box using OpenCV QR detection.

    YOLO first locates the QR.
    A small padded region is then given to OpenCV so it
    has enough surrounding area to detect the QR corners.

    Returns:
        (x1, y1, x2, y2) or None
    """

    height, width = image.shape[:2]

    x1, y1, x2, y2 = yolo_bbox

    # Add padding around YOLO detection
    crop_x1 = max(0, x1 - padding)
    crop_y1 = max(0, y1 - padding)
    crop_x2 = min(width, x2 + padding)
    crop_y2 = min(height, y2 + padding)

    # Crop padded region
    crop = image[
        crop_y1:crop_y2,
        crop_x1:crop_x2
    ]

    if crop.size == 0:
        return None

    # Detect QR inside padded crop
    detector = cv2.QRCodeDetector()
    success, points = detector.detect(crop)

    if not success or points is None:
        return None

    points = points[0].astype(np.int32)

    # Convert crop coordinates back to full-image coordinates
    points[:, 0] += crop_x1
    points[:, 1] += crop_y1

    # Create precise bounding rectangle
    refined_x1 = int(np.min(points[:, 0]))
    refined_y1 = int(np.min(points[:, 1]))
    refined_x2 = int(np.max(points[:, 0]))
    refined_y2 = int(np.max(points[:, 1]))

    return (
        refined_x1,
        refined_y1,
        refined_x2,
        refined_y2
    )