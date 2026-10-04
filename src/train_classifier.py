import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from pathlib import Path


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

DATA_DIR = Path("dataset_classification")

BATCH_SIZE = 16
EPOCHS = 10
IMAGE_SIZE = 224
LEARNING_RATE = 0.001

MODEL_DIR = Path("model")
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "mobilenetv3_xqr.pth"


# --------------------------------------------------
# DEVICE
# --------------------------------------------------

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", device)


# --------------------------------------------------
# IMAGE TRANSFORMS
# --------------------------------------------------

# IMPORTANT:
# Horizontal flipping is intentionally removed.
# The synthetic tampering is specifically placed
# on the left side of the QR boundary.

train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomRotation(8),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# DATASET
# --------------------------------------------------

train_dataset = datasets.ImageFolder(
    DATA_DIR / "train",
    transform=train_transform
)

val_dataset = datasets.ImageFolder(
    DATA_DIR / "val",
    transform=val_transform
)

print("\nClasses:", train_dataset.classes)
print("Training images:", len(train_dataset))
print("Validation images:", len(val_dataset))


# --------------------------------------------------
# DATA LOADERS
# --------------------------------------------------

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# --------------------------------------------------
# MOBILENETV3
# --------------------------------------------------

model = models.mobilenet_v3_small(
    weights="DEFAULT"
)

# Replace the final classifier layer
input_features = model.classifier[-1].in_features

model.classifier[-1] = nn.Linear(
    input_features,
    2
)

model = model.to(device)


# --------------------------------------------------
# LOSS FUNCTION
# --------------------------------------------------

criterion = nn.CrossEntropyLoss()


# --------------------------------------------------
# OPTIMIZER
# --------------------------------------------------

optimizer = optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# --------------------------------------------------
# TRAINING
# --------------------------------------------------

for epoch in range(EPOCHS):

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        # Clear previous gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(images)

        # Calculate loss
        loss = criterion(
            outputs,
            labels
        )

        # Backpropagation
        loss.backward()

        # Update model
        optimizer.step()

        running_loss += loss.item()

        # Calculate training accuracy
        _, predicted = torch.max(
            outputs,
            1
        )

        total += labels.size(0)

        correct += (
            predicted == labels
        ).sum().item()

    train_accuracy = (
        100 * correct / total
    )


    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    model.eval()

    val_correct = 0
    val_total = 0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            _, predicted = torch.max(
                outputs,
                1
            )

            val_total += labels.size(0)

            val_correct += (
                predicted == labels
            ).sum().item()

    val_accuracy = (
        100 * val_correct / val_total
    )


    # --------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------

    print(
        f"Epoch {epoch + 1}/{EPOCHS} | "
        f"Loss: "
        f"{running_loss / len(train_loader):.4f} | "
        f"Train Acc: "
        f"{train_accuracy:.2f}% | "
        f"Val Acc: "
        f"{val_accuracy:.2f}%"
    )


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

torch.save(
    model.state_dict(),
    MODEL_PATH
)

print("\nTraining complete.")
print(
    "Model saved to:",
    MODEL_PATH
)