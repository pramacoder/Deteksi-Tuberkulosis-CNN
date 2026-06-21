import cv2
import numpy as np

IMG_SIZE = (224, 224)
THRESHOLD = 0.35  # Optimal threshold for TB recall >= 0.95

def interpret(prob_tb: float) -> dict:
    label = "TB" if prob_tb >= THRESHOLD else "Normal"
    if prob_tb > 0.8 or prob_tb < 0.2:
        confidence = "High"
    elif prob_tb > 0.6 or prob_tb < 0.4:
        confidence = "Medium"
    else:
        confidence = "Low"
    return {"label": label, "confidence": confidence, "threshold_used": THRESHOLD}

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Load image from bytes, apply CLAHE, central crop, resize, and normalize."""
    # Decode image from bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Invalid image file or format not supported.")
    
    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    
    # Central crop 85%
    h, w = img.shape[:2]
    crop_h, crop_w = int(h * 0.85), int(w * 0.85)
    sh, sw = (h - crop_h) // 2, (w - crop_w) // 2
    img = img[sh:sh+crop_h, sw:sw+crop_w]
    
    # Resize
    img = cv2.resize(img, IMG_SIZE)
    
    # Normalize to [0, 1]
    img = img.astype(np.float32) / 255.0
    
    # Expand dims to (1, 224, 224, 1)
    return np.expand_dims(np.expand_dims(img, -1), 0)
