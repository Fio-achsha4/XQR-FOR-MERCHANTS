from src.classification.mobile_classifier import classify_image


image_path = "data/tampered/tampered_01.png"

result = classify_image(image_path)

print("\n--- MobileNetV3 Result ---")
print("Prediction:", result["class"])
print(f"Confidence: {result['confidence']:.2f}%")
print(f"Genuine probability: {result['genuine_probability']:.2f}%")
print(f"Tampered probability: {result['tampered_probability']:.2f}%")