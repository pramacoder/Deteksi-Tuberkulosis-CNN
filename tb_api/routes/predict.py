from fastapi import APIRouter, UploadFile, File, HTTPException
from schemas.response import PredictResponse
from model.loader import get_model
from model.predictor import preprocess_image, interpret

router = APIRouter()

@router.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        model = get_model()
        
        # Preprocess
        img_array = preprocess_image(contents)
        
        # Predict
        predictions = model.predict(img_array)
        prob_tb = float(predictions[0][1])  # Class 1 is TB
        
        # Interpret
        result = interpret(prob_tb)
        
        return PredictResponse(
            label=result["label"],
            probability=prob_tb,
            confidence=result["confidence"],
            threshold_used=result["threshold_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
