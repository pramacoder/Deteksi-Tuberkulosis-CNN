export interface PredictResponse {
  label: string;
  probability: number;
  confidence: string;
  threshold_used: number;
}

export interface GradcamResponse extends PredictResponse {
  gradcam_image: string; // base64
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function predictImage(file: File): Promise<PredictResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || 'Gagal melakukan prediksi');
  }

  return res.json();
}

export async function predictWithGradcam(file: File): Promise<GradcamResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_URL}/gradcam`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || 'Gagal menghasilkan Grad-CAM');
  }

  return res.json();
}
