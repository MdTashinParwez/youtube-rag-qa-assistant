from fastapi import APIRouter
from pydantic import BaseModel

from app.services.transcript import get_transcript
from app.services.chunker import create_chunks
from app.services.vector_store import ( get_or_create_vector_store,  get_vector_store)
from app.services.rag import create_retriever, generate_answer


router = APIRouter(
    prefix="/api/v1/video",
    tags=["Video"]
)


class AnalyzeRequest(BaseModel):
    videoId: str


class ChatRequest(BaseModel):
    videoId: str
    question: str


@router.post("/analyze")
def analyze_video(data: AnalyzeRequest):

    video_id = data.videoId

    # 1. Get transcript
    transcript = get_transcript(video_id)

    # 2. Create chunks
    chunks = create_chunks(transcript)

    # Temporary quota protection
    chunks = chunks[:10]

    # 3. Create / get vector store
    get_or_create_vector_store(
        video_id,
        chunks
    )

    return {
        "success": True,
        "videoId": video_id,
        "totalChunks": len(chunks),
        "message": "Video analyzed successfully"
    }


@router.post("/chat")
def chat_with_video(data: ChatRequest):

    video_id = data.videoId
    question = data.question

    vector_store = get_vector_store(video_id)

    # Vector store RAM mein nahi hai
    if vector_store is None:

        try:
            transcript = get_transcript(video_id)

            chunks = create_chunks(transcript)

            # Temporary quota protection
            chunks = chunks[:10]

            vector_store = get_or_create_vector_store(
                video_id,
                chunks
            )

        except Exception as e:

            return {
                "success": False,
                "videoId": video_id,
                "message": "Could not prepare this video.",
                "detail": str(e)
            }

    retriever = create_retriever(vector_store)

    relevant_docs = retriever.invoke(question)

    answer = generate_answer(
        relevant_docs,
        question
    )

    return {
        "success": True,
        "videoId": video_id,
        "question": question,
        "answer": answer,
        "sources": [
            {
                "start_time": doc.metadata.get("start_time"),
                "end_time": doc.metadata.get("end_time")
            }
            for doc in relevant_docs
        ]
    }


