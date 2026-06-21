from pydantic import BaseModel

class PredictResponse(BaseModel):
    label: str          # "TB" atau "Normal"
    probability: float  # P(TB), antara 0-1
    confidence: str     # "High" / "Medium" / "Low"
    threshold_used: float

class GradcamResponse(PredictResponse):
    gradcam_image: str  # base64 encoded PNG
