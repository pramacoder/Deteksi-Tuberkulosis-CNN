import os
from dotenv import load_dotenv

load_dotenv()

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
        
        try:
            import keras
            loaded_model = keras.models.load_model(MODEL_PATH)
            print("Model loaded successfully with Keras.")
        except Exception as e:
            print(f"Keras load fallback ({e}). Using NumpyBasicCNN engine.")
            from model.numpy_engine import NumpyBasicCNN
            loaded_model = NumpyBasicCNN(MODEL_PATH)
            print("Model loaded successfully with NumPy engine.")
    return loaded_model

def get_model():
    if loaded_model is None:
        return load_model()
    return loaded_model
