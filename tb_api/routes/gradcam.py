from fastapi import APIRouter, UploadFile, File, HTTPException
from schemas.response import GradcamResponse
from model.loader import get_model
from model.predictor import preprocess_image, interpret
from model.gradcam import get_gradcam_heatmap, generate_gradcam_overlay

router = APIRouter()

@router.post("/gradcam", response_model=GradcamResponse)
async def gradcam(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        model = get_model()
        
        # Preprocess
        img_array = preprocess_image(contents)
        
        # Predict
        predictions = model.predict(img_array)
        prob_tb = float(predictions[0][1])
        
        # Interpret
        result = interpret(prob_tb)
        
        # Generate Grad-CAM
        heatmap = get_gradcam_heatmap(model, img_array)
        gradcam_base64 = generate_gradcam_overlay(contents, heatmap)
        
        return GradcamResponse(
            label=result["label"],
            probability=prob_tb,
            confidence=result["confidence"],
            threshold_used=result["threshold_used"],
            gradcam_image=f"data:image/png;base64,{gradcam_base64}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
