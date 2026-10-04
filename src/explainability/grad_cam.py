import cv2
import torch
import torch.nn as nn
import numpy as np

from pathlib import Path
from PIL import Image
from torchvision import models, transforms

from src.preprocessing.yolo_detector import detect_qr


MODEL_PATH = Path("model/mobilenetv3_xqr.pth")
IMAGE_SIZE = 224

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# --------------------------------------------------
# Load MobileNetV3
# --------------------------------------------------

def load_model():

    model = models.mobilenet_v3_small(
        weights=None
    )

    input_features = model.classifier[-1].in_features

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


# --------------------------------------------------
# Image preprocessing
# --------------------------------------------------

transform = transforms.Compose([
    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# Crop QR + surrounding margin
# --------------------------------------------------

def crop_qr_region(image_path):

    image = Image.open(
        image_path
    ).convert("RGB")

    bbox = detect_qr(
        image_path
    )

    if bbox is None:

        print(
            "YOLO could not detect the QR."
        )

        return image

    x1, y1, x2, y2 = bbox

    width, height = image.size

    margin = 45

    x1 = max(
        0,
        x1 - margin
    )

    y1 = max(
        0,
        y1 - margin
    )

    x2 = min(
        width,
        x2 + margin
    )

    y2 = min(
        height,
        y2 + margin
    )

    return image.crop(
        (x1, y1, x2, y2)
    )


# --------------------------------------------------
# Grad-CAM
# --------------------------------------------------

def generate_gradcam(image_path):

    model = load_model()

    # MobileNetV3 Small final convolutional layer
    target_layer = model.features[-1]

    activations = []
    gradients = []

    def forward_hook(
        module,
        input,
        output
    ):
        activations.append(
            output.detach()
        )

    def backward_hook(
        module,
        grad_input,
        grad_output
    ):
        gradients.append(
            grad_output[0].detach()
        )

    forward_handle = target_layer.register_forward_hook(
        forward_hook
    )

    backward_handle = target_layer.register_full_backward_hook(
        backward_hook
    )

    try:

        image = crop_qr_region(
            image_path
        )

        original_image = image.copy()

        image_tensor = transform(
            image
        ).unsqueeze(0).to(device)

        # Forward pass
        output = model(
            image_tensor
        )

        probabilities = torch.softmax(
            output,
            dim=1
        )[0]

        predicted_class = torch.argmax(
            probabilities
        ).item()

        # Clear previous gradients
        model.zero_grad()

        # Backpropagate predicted class
        output[0, predicted_class].backward()

        activation = activations[0]
        gradient = gradients[0]

        # Global average pooling of gradients
        weights = gradient.mean(
            dim=(2, 3),
            keepdim=True
        )

        # Weighted activation maps
        cam = (
            weights * activation
        ).sum(
            dim=1
        ).squeeze()

        cam = torch.relu(
            cam
        )

        cam = cam.cpu().numpy()

        # Normalize CAM
        cam_min = cam.min()
        cam_max = cam.max()

        if cam_max - cam_min != 0:

            cam = (
                cam - cam_min
            ) / (
                cam_max - cam_min
            )

        else:

            cam = np.zeros_like(
                cam
            )

        # Convert to 0-255
        cam = np.uint8(
            cam * 255
        )

        # Resize heatmap to original crop
        cam = cv2.resize(
            cam,
            original_image.size
        )

        heatmap = cv2.applyColorMap(
            cam,
            cv2.COLORMAP_JET
        )

        original = cv2.cvtColor(
            np.array(original_image),
            cv2.COLOR_RGB2BGR
        )

        overlay = cv2.addWeighted(
            original,
            0.55,
            heatmap,
            0.45,
            0
        )

        return {
            "predicted_class": predicted_class,
            "genuine_probability":
                probabilities[0].item() * 100,
            "tampered_probability":
                probabilities[1].item() * 100,
            "heatmap": overlay
        }

    finally:

        forward_handle.remove()
        backward_handle.remove()