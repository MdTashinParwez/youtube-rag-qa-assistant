from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/video",
    tags=["Video"]
)


@router.post("/analyze")
def analyze_video():
    return {
        "message": "Video analysis endpoint"
    }


@router.post("/chat")
def chat_with_video():
    return {
        "message": "Video chat endpoint"
    }