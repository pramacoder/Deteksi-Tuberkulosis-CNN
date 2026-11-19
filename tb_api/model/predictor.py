import cv2
import numpy as np
import io
from PIL import Image

IMG_SIZE = (224, 224)
THRESHOLD = 0.35  # Optimal threshold configured for TB screening (Recall >= 0.95)

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
    """
    Resolution-invariant preprocessing pipeline (Tahap 1):
    1. Decode grayscale image
    2. Central crop 88% (removes outer corner markers while preserving upper lung apices)
    3. Resize to (224, 224) using anti-aliased INTER_AREA BEFORE applying CLAHE
    4. Apply CLAHE (8x8 grid on standardized 224x224 resolution)
    5. Normalize to [0, 1]
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert('L')
            img = np.array(pil_img)
        except Exception:
            raise ValueError("Invalid image file or format not supported.")
    
    # 1. Central crop 88% (preserves upper lung apices while trimming edge markers)
    h, w = img.shape[:2]
    crop_h, crop_w = int(h * 0.88), int(w * 0.88)
    sh, sw = (h - crop_h) // 2, (w - crop_w) // 2
    img = img[sh:sh+crop_h, sw:sw+crop_w]
    
    # 2. Resize to 224x224 BEFORE CLAHE (prevents resolution/JPEG block shortcut)
    interp = cv2.INTER_AREA if (crop_h > IMG_SIZE[0] or crop_w > IMG_SIZE[1]) else cv2.INTER_LINEAR
    img = cv2.resize(img, IMG_SIZE, interpolation=interp)
    
    # 3. Apply CLAHE on standardized 224x224 grid
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    
    # 4. Normalize to [0, 1]
    img = img.astype(np.float32) / 255.0
    
    # Expand dims to (1, 224, 224, 1)
    return np.expand_dims(np.expand_dims(img, -1), 0)
