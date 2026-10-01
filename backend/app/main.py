from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from app.services.transcript import get_transcript
from app.services.chunker import create_chunks
from app.services.chunker import create_chunks
from app.services.vector_store import get_or_create_vector_store
from app.services.rag import create_retriever, generate_answer
from fastapi import FastAPI
from app.routes.video import router as video_router

app = FastAPI()

app.include_router(video_router)

import os

load_dotenv()

app = FastAPI()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
)

@app.get("/")
def root():
    return {
        "message": "YouTube AI Assistant API is running"
    }


@app.get("/test-gemini")
def test_gemini():

    response = llm.invoke(
        "Say hello in one short sentence."
    )

    return {
        "response": response.content
    }

@app.get("/test-transcript/{video_id}")
def test_transcript(video_id: str):

    transcript = get_transcript(video_id)

    return {
        "videoId": video_id,
        "totalSnippets": len(transcript),
        "transcript": transcript[:5]
    }

@app.get("/test-chunks/{video_id}")
def test_chunks(video_id: str):
    transcript = get_transcript(video_id)

    chunks = create_chunks(transcript)

    return {
        "videoId": video_id,
        "totalChunks": len(chunks),
        "firstChunk": chunks[0].page_content,
        "firstChunkMetadata": chunks[0].metadata,
        "lastChunkMetadata": chunks[-1].metadata
    }


@app.get("/test-vector-store/{video_id}")
def test_vector_store(video_id: str):

    transcript = get_transcript(video_id)

    chunks = create_chunks(transcript)

    # Temporary quota test
    chunks = chunks[:10]

    vector_store = create_vector_store(chunks)

    return {
        "videoId": video_id,
        "totalChunks": len(chunks),
        "message": "Vector store created successfully"
    }

@app.get("/test-question/{video_id}")
def test_question(video_id: str, question: str):

    transcript = get_transcript(video_id)

    chunks = create_chunks(transcript)

    # Temporary quota protection
    chunks = chunks[:10]

    vector_store = get_or_create_vector_store(
        video_id,
        chunks
    )

    retriever = create_retriever(vector_store)

    relevant_docs = retriever.invoke(question)

    answer = generate_answer(
        relevant_docs,
        question
    )

    return {
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









