import os
import keras
from dotenv import load_dotenv

load_dotenv()

# Look for model file in the local directory first, then fallback to environment variable or parent directory
LOCAL_PATH = os.path.join(os.path.dirname(__file__), "best_BasicCNN_v2_fixed.keras")
if os.path.exists(LOCAL_PATH):
    MODEL_PATH = LOCAL_PATH
else:
    MODEL_PATH = os.getenv("MODEL_PATH", "../outputs/best_BasicCNN_v2_fixed.keras")
loaded_model = None

def load_model():
    global loaded_model
    if loaded_model is None:
        print(f"Loading model from {MODEL_PATH}...")
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        loaded_model = keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully.")
    return loaded_model

def get_model():
    if loaded_model is None:
        return load_model()
    return loaded_model
