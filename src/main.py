from fastapi import FastAPI
from src.api.endpoints import router as api_router
# from src.interfaces.gradio_ui import gradio_app
import os

print(os.getcwd())
app = FastAPI()
app.include_router(api_router, prefix="/api")
# app.mount("/gradio", gradio_app)

@app.get("/")
async def root():
    return {"message": "LinkedIn Bot Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8054)