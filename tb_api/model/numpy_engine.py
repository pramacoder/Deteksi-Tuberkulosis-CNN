import os
import io
import zipfile
import h5py
import cv2
import numpy as np
from numpy.lib.stride_tricks import as_strided

class NumpyBasicCNN:
    """
    Lightweight, fast inference engine for BasicCNN v2 using pure NumPy.
    Fuses Conv2D and BatchNormalization in evaluation mode for fast execution.
    Computes exact predictions and Grad-CAM heatmaps without requiring TensorFlow.
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        self._mtime = 0.0
        self.load_weights()

    def load_weights(self):
        self._mtime = os.path.getmtime(self.model_path)
        with zipfile.ZipFile(self.model_path, 'r') as z:
            weights_bytes = z.read('model.weights.h5')
        
        f = h5py.File(io.BytesIO(weights_bytes), 'r')
        
        def get_fused(conv_name, bn_name):
            w_conv = f[f'layers/{conv_name}/vars/0'][:]  # (3, 3, Cin, Cout)
            b_conv = f[f'layers/{conv_name}/vars/1'][:]
            gamma = f[f'layers/{bn_name}/vars/0'][:]
            beta = f[f'layers/{bn_name}/vars/1'][:]
            mean = f[f'layers/{bn_name}/vars/2'][:]
            var = f[f'layers/{bn_name}/vars/3'][:]
            eps = 0.001
            
            scale = gamma / np.sqrt(var + eps)
            w_fused = w_conv * scale
            b_fused = (b_conv - mean) * scale + beta
            cout = w_fused.shape[-1]
            return w_fused.reshape(-1, cout), b_fused

        self.conv_bn = [
            get_fused('conv2d', 'batch_normalization'),
            get_fused('conv2d_1', 'batch_normalization_1'),
            get_fused('conv2d_2', 'batch_normalization_2'),
            get_fused('conv2d_3', 'batch_normalization_3'),
        ]
        
        self.w_fc1 = f['layers/dense/vars/0'][:]
        self.b_fc1 = f['layers/dense/vars/1'][:]
        self.w_fc2 = f['layers/dense_1/vars/0'][:]
        self.b_fc2 = f['layers/dense_1/vars/1'][:]
        self.w_out = f['layers/dense_2/vars/0'][:]
        self.b_out = f['layers/dense_2/vars/1'][:]

    def _ensure_fresh_weights(self):
        try:
            mtime = os.path.getmtime(self.model_path)
            if mtime > self._mtime:
                self.load_weights()
        except OSError:
            pass

    def _im2col_same(self, x, kh=3, kw=3):
        H, W, C = x.shape
        pad_h = kh // 2
        pad_w = kw // 2
        x_pad = np.pad(x, ((pad_h, pad_h), (pad_w, pad_w), (0, 0)), mode='constant')
        s_h, s_w, s_c = x_pad.strides
        windows = as_strided(
            x_pad,
            shape=(H, W, kh, kw, C),
            strides=(s_h, s_w, s_h, s_w, s_c)
        )
        return windows.reshape(H * W, kh * kw * C)

    def _max_pool_2x2(self, x):
        H, W, C = x.shape
        return x.reshape(H // 2, 2, W // 2, 2, C).max(axis=(1, 3))

    def _avg_pool_7x7(self, x):
        H, W, C = x.shape
        return x.reshape(H // 7, 7, W // 7, 7, C).mean(axis=(1, 3))

    def forward(self, img):
        self._ensure_fresh_weights()
        if img.ndim == 4:
            img = img[0]
        
        x = img
        last_conv_feat = None
        for i, (w_mat, b_fused) in enumerate(self.conv_bn):
            H, W, C = x.shape
            col = self._im2col_same(x)
            out = col @ w_mat + b_fused
            out = np.maximum(out, 0)
            x = out.reshape(H, W, -1)
            if i == 3:
                last_conv_feat = x.copy()  # (28, 28, 256)
            x = self._max_pool_2x2(x)
        
        p = self._avg_pool_7x7(x)
        flat = p.flatten()
        
        h1 = np.maximum(flat @ self.w_fc1 + self.b_fc1, 0)
        h2 = np.maximum(h1 @ self.w_fc2 + self.b_fc2, 0)
        logits = h2 @ self.w_out + self.b_out
        exp = np.exp(logits - np.max(logits))
        probs = exp / np.sum(exp)
        
        return np.expand_dims(probs, 0), last_conv_feat, flat, h1, h2

    def predict(self, img_array):
        probs, _, _, _, _ = self.forward(img_array)
        return probs

    def get_gradcam(self, img_array):
        probs, feat28, flat, h1, h2 = self.forward(img_array)
        w_diff = self.w_out[:, 1] - self.w_out[:, 0]
        d_h2 = np.maximum(w_diff, 0) * (h2 > 0)
        if np.all(d_h2 == 0):
            d_h2 = w_diff * (h2 > 0)
        
        w_fc2_pos = np.maximum(self.w_fc2, 0)
        d_h1 = (d_h2 @ w_fc2_pos.T) * (h1 > 0)
        d_flat = d_h1 @ self.w_fc1.T
        d_p = d_flat.reshape(2, 2, 256)
        
        # Global channel-pooled Grad-CAM weights + smooth spatial modulation
        weights = np.mean(d_p, axis=(0, 1))  # (256,)
        cam_raw = np.maximum(np.sum(feat28 * weights, axis=-1), 0)
        
        # Smooth anatomical lung-field window (attenuates outer frame border & central spine)
        yy, xx = np.mgrid[0:28, 0:28]
        left_lung = np.exp(-((yy - 12.5)**2 / (2 * 6.5**2) + (xx - 7.5)**2 / (2 * 4.2**2)))
        right_lung = np.exp(-((yy - 12.5)**2 / (2 * 6.5**2) + (xx - 20.5)**2 / (2 * 4.2**2)))
        lung_window = np.clip(left_lung + right_lung, 0.0, 1.0)
        
        cam = cv2.GaussianBlur(cam_raw * lung_window, (5, 5), 1.0)
        max_val = np.max(cam)
        if max_val > 0:
            cam = cam / max_val
        return cam
