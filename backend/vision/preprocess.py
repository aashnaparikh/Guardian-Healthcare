import cv2
import numpy as np

def load_xray(image_path: str) -> np.ndarray:
    """Load an X-ray image in grayscale."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at: {image_path}")
    print(f"✓ Loaded image: {img.shape} pixels")
    return img

def apply_clahe(img: np.ndarray) -> np.ndarray:
    """CLAHE enhances local contrast so subtle abnormalities become visible."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)
    print("✓ Applied CLAHE contrast enhancement")
    return enhanced

def denoise(img: np.ndarray) -> np.ndarray:
    """Remove noise using Gaussian blur while keeping edges sharp."""
    denoised = cv2.GaussianBlur(img, (3, 3), 0)
    print("✓ Applied Gaussian denoising")
    return denoised

def resize(img: np.ndarray, size: tuple = (224, 224)) -> np.ndarray:
    """Resize to 224x224 — standard input size for ResNet."""
    resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    print(f"✓ Resized to {size}")
    return resized

def normalize(img: np.ndarray) -> np.ndarray:
    """Scale pixel values to 0-1 range for neural network input."""
    normalized = img.astype(np.float32) / 255.0
    print("✓ Normalized pixel values to [0, 1]")
    return normalized

def preprocess_xray(image_path: str) -> np.ndarray:
    """Full pipeline: Load → CLAHE → Denoise → Resize → Normalize"""
    print(f"\n--- Guardian Preprocessing Pipeline ---")
    print(f"Input: {image_path}\n")
    img = load_xray(image_path)
    img = apply_clahe(img)
    img = denoise(img)
    img = resize(img)
    img = normalize(img)
    print(f"\n✓ Pipeline complete. Output shape: {img.shape}, dtype: {img.dtype}")
    print(f"  Pixel range: [{img.min():.3f}, {img.max():.3f}]")
    return img

def save_preprocessed(img: np.ndarray, output_path: str):
    """Save processed image for visual inspection."""
    save_img = (img * 255).astype(np.uint8)
    cv2.imwrite(output_path, save_img)
    print(f"✓ Saved preprocessed image to: {output_path}")

if __name__ == "__main__":
    processed = preprocess_xray("sample_xray.jpg")
    save_preprocessed(processed, "sample_xray_processed.jpg")
    print("\n🩺 Guardian Vision Pipeline: SMOKE TEST PASSED")