import cv2
import numpy as np


def create_margin_mask(image, bbox, inner_margin=15, outer_margin=45):
    """
    Create a mask for the area immediately outside the QR bounding box.

    bbox format:
        (x1, y1, x2, y2)
    """

    height, width = image.shape[:2]

    x1, y1, x2, y2 = bbox

    # Make sure coordinates stay inside the image
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)

    # Create QR bounding-box mask
    qr_mask = np.zeros((height, width), dtype=np.uint8)
    qr_mask[y1:y2, x1:x2] = 255

    # Expand the QR area
    inner_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (inner_margin * 2 + 1, inner_margin * 2 + 1)
    )

    outer_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (outer_margin * 2 + 1, outer_margin * 2 + 1)
    )

    inner_area = cv2.dilate(qr_mask, inner_kernel)
    outer_area = cv2.dilate(qr_mask, outer_kernel)

    # Keep only the ring between inner and outer boundaries
    margin_mask = cv2.subtract(outer_area, inner_area)

    return margin_mask