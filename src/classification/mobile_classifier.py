import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from pathlib import Path

from src.preprocessing.yolo_detector import detect_qr


MODEL_PATH = Path("model/mobilenetv3_xqr.pth")

CLASS_NAMES = ["genuine", "tampered"]

IMAGE_SIZE = 224

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def load_model():
    """Load the trained MobileNetV3 model."""

    model = models.mobilenet_v3_small(
        weights=None
    )

    input_features = (
        model.classifier[-1].in_features
    )

    model.classifier[-1] = nn.Linear(
        input_features,
        2
    )

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location=device
        )
    )

    model.to(device)
    model.eval()

    return model


def crop_qr_region(image_path):
    """
    Detect the QR using YOLO and crop the QR
    together with a surrounding margin.
    """

    image = Image.open(
        image_path
    ).convert("RGB")

    bbox = detect_qr(image_path)

    if bbox is None:
        print(
            "YOLO could not detect the QR. "
            "Using the full image."
        )
        return image

    x1, y1, x2, y2 = bbox

    width, height = image.size

    # Add surrounding margin so that
    # tampering near the QR boundary is visible.
    margin = 80

    x1 = max(0, x1 - margin)
    y1 = max(0, y1 - margin)
    x2 = min(width, x2 + margin)
    y2 = min(height, y2 + margin)

    cropped = image.crop(
        (x1, y1, x2, y2)
    )

    return cropped


def classify_image(image_path):
    """Classify the localized QR region."""

    model = load_model()

    image = crop_qr_region(
        image_path
    )

    image_tensor = transform(image)

    image_tensor = image_tensor.unsqueeze(0)

    image_tensor = image_tensor.to(device)

    with torch.no_grad():

        output = model(image_tensor)

        probabilities = torch.softmax(
            output,
            dim=1
        )[0]

    predicted_index = torch.argmax(
        probabilities
    ).item()

    predicted_class = (
        CLASS_NAMES[predicted_index]
    )

    confidence = (
        probabilities[predicted_index].item()
        * 100
    )

    return {
        "class": predicted_class,
        "confidence": confidence,
        "genuine_probability":
            probabilities[0].item() * 100,
        "tampered_probability":
            probabilities[1].item() * 100
    }