from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routes.video import router as video_router


app = FastAPI(
    title="YouTube AI Assistant API",
    description="AI-powered YouTube video Q&A backend",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(video_router)


@app.get("/")
def root():
    return {
        "message": "YouTube AI Assistant API is running"
    }