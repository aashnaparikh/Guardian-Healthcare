import torch
import torch.nn as nn
from torchvision import models
from torchvision import transforms
import numpy as np

# Labels matching the NIH ChestX-ray14 dataset
CONDITION_LABELS = [
    "No Finding", "Atelectasis", "Cardiomegaly", "Effusion",
    "Infiltration", "Mass", "Nodule", "Pneumonia",
    "Pneumothorax", "Consolidation", "Edema", "Emphysema",
    "Fibrosis", "Pleural Thickening", "Hernia"
]
NUM_CLASSES = len(CONDITION_LABELS)


def build_model(pretrained: bool = True) -> nn.Module:
    """
    Load ResNet-18 pretrained on ImageNet, then replace the final
    layer to output 15 classes (NIH ChestX-ray14 conditions).
    This is called 'transfer learning' — we borrow general visual
    features (edges, textures) and retrain the head for X-rays.
    """
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT if pretrained else None)

    # ResNet-18's final layer outputs 1000 ImageNet classes.
    # We replace it with our own 15-class layer.
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=0.3),           # Regularization to prevent overfitting
        nn.Linear(in_features, NUM_CLASSES),
        nn.Sigmoid()                  # Multi-label: each condition is independent
    )

    print(f"✓ Built ResNet-18 with {NUM_CLASSES} output classes")
    print(f"  Final layer: {in_features} → {NUM_CLASSES}")
    return model


def preprocess_for_model(img_array: np.ndarray) -> torch.Tensor:
    """
    Convert our preprocessed numpy array into a PyTorch tensor
    that ResNet-18 expects: shape [1, 3, 224, 224]
    ResNet expects 3 channels (RGB), so we stack the grayscale 3x.
    """
    # Stack grayscale into 3 channels
    img_3ch = np.stack([img_array, img_array, img_array], axis=0)  # (3, 224, 224)

    # ImageNet normalization — ResNet was trained with these exact values
    mean = np.array([0.485, 0.456, 0.406]).reshape(3, 1, 1)
    std  = np.array([0.229, 0.224, 0.225]).reshape(3, 1, 1)
    img_norm = (img_3ch - mean) / std

    # Add batch dimension: (3, 224, 224) → (1, 3, 224, 224)
    tensor = torch.FloatTensor(img_norm).unsqueeze(0)
    return tensor


def run_inference(model: nn.Module, tensor: torch.Tensor) -> dict:
    """
    Run a forward pass and return confidence scores per condition.
    """
    model.eval()
    with torch.no_grad():
        outputs = model(tensor)  # Shape: [1, 15]
        scores = outputs.squeeze().numpy()

    results = {label: float(score) for label, score in zip(CONDITION_LABELS, scores)}
    return results


def print_results(results: dict, threshold: float = 0.3):
    """Display results in a clean format."""
    print("\n--- Guardian Diagnostic Results ---")
    flagged = {k: v for k, v in results.items() if v >= threshold and k != "No Finding"}

    if not flagged:
        print(f"✓ No Finding — all conditions below {threshold:.0%} threshold")
    else:
        print(f"⚠️  Flagged conditions (confidence ≥ {threshold:.0%}):")
        for condition, score in sorted(flagged.items(), key=lambda x: -x[1]):
            bar = "█" * int(score * 20)
            print(f"  {condition:<22} {score:.1%}  {bar}")

    print(f"\n  Top condition: {max(results, key=results.get)} "
          f"({max(results.values()):.1%})")


# --- Smoke test ---
if __name__ == "__main__":
    from preprocess import preprocess_xray
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

    print("Loading model...")
    model = build_model(pretrained=True)
    print(f"✓ Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    print("\nPreprocessing image...")
    from backend.vision.preprocess import preprocess_xray
    img = preprocess_xray("sample_xray.jpg")

    print("\nRunning inference...")
    tensor = preprocess_for_model(img)
    results = run_inference(model, tensor)
    print_results(results)

    print("\n🧠 Guardian CNN: SMOKE TEST PASSED")