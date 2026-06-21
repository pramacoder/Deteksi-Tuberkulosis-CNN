import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.loader import load_model, get_model
from routes import predict, gradcam

app = FastAPI(title="TB Detection API", version="1.0.0")

# CORS config for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Usually configure for specific frontend domain like http://localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Pre-load the model when server starts
    load_model()

@app.get("/")
def read_root():
    return {"message": "Welcome to TB Detection API"}

@app.get("/health")
def health_check():
    model_loaded = get_model() is not None
    return {"status": "ok", "model_loaded": model_loaded}

# Include routers
app.include_router(predict.router, tags=["Predict"])
app.include_router(gradcam.router, tags=["Grad-CAM"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
