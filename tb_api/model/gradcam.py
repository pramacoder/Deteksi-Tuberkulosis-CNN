import cv2
import numpy as np
import base64

IMG_SIZE = (224, 224)
LAST_CONV_LAYER = 'block4_conv'

def get_gradcam_heatmap(model, img_array, last_conv_layer_name=LAST_CONV_LAYER):
    """Generate Grad-CAM heatmap for BasicCNN."""
    if hasattr(model, 'get_gradcam'):
        return model.get_gradcam(img_array)
    
    import tensorflow as tf
    import keras
    grad_model = keras.models.Model(
        inputs=model.input,
        outputs=[model.get_layer(last_conv_layer_name).output, model.output]
    )
    
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, 1]
    
    grads = tape.gradient(loss, conv_outputs)
    if grads is None:
        return np.zeros(IMG_SIZE)
    
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()

def generate_gradcam_overlay(image_bytes: bytes, heatmap: np.ndarray, alpha=0.45) -> str:
    """Generate base64 encoded PNG of the original image with Grad-CAM overlay."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    orig_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if orig_img is None:
        from PIL import Image
        import io
        pil_img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        orig_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
    orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
    
    orig_img = cv2.resize(orig_img, IMG_SIZE)
    
    heatmap_resized = cv2.resize(heatmap, IMG_SIZE)
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    superimposed = np.uint8(heatmap_colored * alpha + orig_img * (1 - alpha))
    
    _, buffer = cv2.imencode('.png', cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))
    base64_str = base64.b64encode(buffer).decode('utf-8')
    return base64_str
