from pathlib import Path
import cv2

from src.explainability.grad_cam import generate_gradcam


# Test the actual tampered XQR image
image_path = Path(
    "data/tampered/tampered_01.png"
)

result = generate_gradcam(
    image_path
)

print("\n--- Grad-CAM Result ---")

print(
    f"Prediction class: "
    f"{result['predicted_class']}"
)

print(
    f"Genuine probability: "
    f"{result['genuine_probability']:.2f}%"
)

print(
    f"Tampered probability: "
    f"{result['tampered_probability']:.2f}%"
)


# Save Grad-CAM visualization
output_path = Path(
    "results/heatmaps/tampered_gradcam.png"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

cv2.imwrite(
    str(output_path),
    result["heatmap"]
)

print(
    f"\nGrad-CAM saved to: "
    f"{output_path}"
)