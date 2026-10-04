import qrcode
import cv2
from pathlib import Path

# Project folders
genuine_folder = Path("data/genuine")
tampered_folder = Path("data/tampered")

genuine_folder.mkdir(parents=True, exist_ok=True)
tampered_folder.mkdir(parents=True, exist_ok=True)

# SAFE FAKE PAYMENT INFORMATION
fake_upi = "xqr.demo@fake"
fake_name = "XQR Demo Merchant"

# Create QR
qr = qrcode.QRCode(
    version=4,
    box_size=10,
    border=4
)

qr.add_data(f"upi://pay?pa={fake_upi}&pn={fake_name}")
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

# Save genuine QR
genuine_output = genuine_folder / "genuine_01.png"
img.save(genuine_output)

# Create tampered version
tampered = img.convert("RGB")

from PIL import ImageDraw

# Simulate printing/sticker bleeding into the QR quiet zone
draw = ImageDraw.Draw(tampered)

draw.rectangle(
    [25, 145, 48, 175],
    fill=(40, 40, 40)
)

# Rotate by about 2.5 degrees
tampered = tampered.rotate(
    2.5,
    expand=True,
    fillcolor=(245, 245, 245)
)

# Add normal print noise to the whole image
import numpy as np
from PIL import Image, ImageEnhance

array = np.array(tampered).astype(np.int16)

noise = np.random.normal(
    0,
    8,
    array.shape
)

array = np.clip(
    array + noise,
    0,
    255
).astype(np.uint8)

tampered = Image.fromarray(array)


# -----------------------------------------
# Add stronger abnormal noise around the QR
# -----------------------------------------

tampered_array = np.array(tampered).copy()

height, width, _ = tampered_array.shape

# Noise around the outer QR/margin area
rng = np.random.default_rng(42)

margin_noise = rng.normal(
    0,
    35,
    (height, width, 1)
)

# Apply stronger noise only to the image margin
# while keeping the QR itself mostly unchanged.
margin_mask = np.zeros(
    (height, width),
    dtype=np.uint8
)

cv2.rectangle(
    margin_mask,
    (20, 20),
    (width - 20, height - 20),
    255,
    thickness=12
)

noise_area = margin_mask > 0

tampered_array[noise_area] = np.clip(
    tampered_array[noise_area].astype(np.int16)
    + margin_noise[noise_area],
    0,
    255
).astype(np.uint8)

tampered = Image.fromarray(tampered_array)

array = np.clip(array + noise, 0, 255).astype(np.uint8)

tampered = Image.fromarray(array)

# Slightly change contrast
tampered = ImageEnhance.Contrast(tampered).enhance(0.92)

# Save tampered QR
tampered_output = tampered_folder / "tampered_01.png"
tampered.save(tampered_output)

print("Genuine QR created!")
print(f"Saved at: {genuine_output}")

print("Tampered QR created!")
print(f"Saved at: {tampered_output}")
