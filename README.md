# VideoMind AI

> An AI-powered Chrome extension that lets you ask questions about YouTube videos and get grounded answers from the video's transcript.

VideoMind AI combines **YouTube transcript extraction, semantic chunking, Gemini embeddings, FAISS vector search, and Gemini LLMs** to build a Retrieval-Augmented Generation (RAG) pipeline for YouTube videos.

Instead of manually searching through a long video, users can ask questions such as:

* What are the main concepts discussed?
* Explain this topic like I'm a beginner.
* Why is this concept important?
* Summarize this part of the video.

The assistant retrieves the most relevant transcript sections and uses them as context for generating the answer.

---

## Features

### 🎥 YouTube Video Detection

Automatically detects the currently open YouTube video through the Chrome extension.

### 📝 Transcript-Based Q&A

Fetches the video's transcript and uses it as the primary knowledge source for answering questions.

### 🧩 Timestamp-Aware Chunking

The transcript is divided into chunks while preserving:

* Start timestamp
* End timestamp
* Transcript content

This allows retrieved information to remain connected to its location in the original video.

### 🔎 Semantic Search

Transcript chunks are converted into vector embeddings using:

**Google Gemini Embeddings**

The embeddings are stored in a **FAISS vector store** for similarity-based retrieval.

### 🤖 RAG-Powered Answers

When a user asks a question:

1. The question is converted into a semantic representation.
2. Relevant transcript chunks are retrieved.
3. Retrieved chunks are passed to Gemini.
4. Gemini generates an answer grounded in the retrieved video content.

### ⏱️ Timestamp Sources

Every generated answer can contain source timestamps.

For example:

```text
Sources
00:35
01:22
03:47
```

Clicking a timestamp seeks the YouTube video directly to that position.

### 💬 Chat Interface

Users can ask multiple questions about the same video without leaving the extension.

### ✨ Markdown Support

AI responses support readable Markdown formatting including:

* Headings
* Bold text
* Lists
* Paragraphs
* Code formatting

### 🔄 Automatic Video Switching

When the user navigates to another YouTube video:

* The new video ID is detected.
* The new transcript is analyzed.
* The previous chat is cleared.
* A new video-specific Q&A session starts.

---

# Architecture

```text
                    ┌─────────────────────────┐
                    │      YouTube Video      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Chrome Extension     │
                    │      React + Vite        │
                    │    Chrome Side Panel     │
                    └────────────┬────────────┘
                                 │
                                 │ HTTP API
                                 ▼
                    ┌─────────────────────────┐
                    │       FastAPI            │
                    │        Backend           │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌──────────────────┐      ┌──────────────────┐
          │ YouTube          │      │      RAG         │
          │ Transcript       │      │     Pipeline     │
          └────────┬─────────┘      └────────┬─────────┘
                   │                         │
                   ▼                         ▼
          ┌──────────────────┐      ┌──────────────────┐
          │ Timestamp-aware  │      │ Gemini Embedding │
          │ Chunking         │      └────────┬─────────┘
          └────────┬─────────┘               │
                   │                         ▼
                   │                ┌──────────────────┐
                   │                │      FAISS       │
                   │                │  Vector Store    │
                   │                └────────┬─────────┘
                   │                         │
                   │                         ▼
                   │                ┌──────────────────┐
                   └───────────────►│    Retriever     │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   Gemini LLM     │
                                    │ Answer Generation│
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │ Answer + Sources │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │ Chrome Side Panel│
                                    └──────────────────┘
```

---

# How It Works

## 1. Detect the YouTube Video

The content script monitors the current YouTube page and extracts the video ID from the URL.

```text
YouTube URL
     ↓
Extract video ID
     ↓
Send video ID to Chrome service worker
     ↓
Side panel receives video ID
```

---

## 2. Fetch the Transcript

The FastAPI backend receives the video ID and fetches the available transcript.

Each transcript item contains timing information:

```json
{
  "text": "Example transcript text",
  "start": 35.2,
  "duration": 4.8
}
```

The timestamp information is preserved throughout the pipeline.

---

## 3. Create Transcript Chunks

Long transcripts are divided into manageable chunks.

Each chunk becomes a LangChain `Document` containing:

```text
page_content
metadata.start_time
metadata.end_time
```

Example:

```text
Chunk:
"Vibe coding is a new way of building software..."

Metadata:
start_time: 35.2
end_time: 58.7
```

The metadata later becomes the source information returned to the extension.

---

## 4. Generate Embeddings

Each transcript chunk is converted into a vector using:

```text
Gemini Embedding
models/gemini-embedding-001
```

These vectors represent the semantic meaning of the transcript chunks.

---

## 5. Store Vectors in FAISS

The generated embeddings are stored in a FAISS vector store.

FAISS allows the system to efficiently search for transcript chunks that are semantically similar to the user's question.

---

## 6. Retrieve Relevant Context

When the user asks:

```text
What is vibe coding?
```

the question is compared against the transcript embeddings.

The system retrieves the most relevant chunks.

Current retrieval configuration:

```text
search_type: similarity
k: 4
```

So the RAG pipeline retrieves up to four relevant transcript documents.

---

## 7. Generate the Answer

The retrieved transcript chunks are passed to Gemini along with a structured prompt.

The prompt instructs the model to:

* Answer the exact question.
* Use only the provided video context.
* Avoid inventing information.
* Synthesize information instead of blindly copying transcript text.
* Keep answers concise and useful.
* Return a fallback response when the context does not contain enough information.

This creates the final grounded answer.

---

## 8. Return Sources

The backend returns both:

```json
{
  "answer": "...",
  "sources": [
    {
      "start_time": 35.2,
      "end_time": 58.7
    }
  ]
}
```

The extension converts the timestamp into a clickable source button.

Clicking it sends a message back through the Chrome extension:

```text
Side Panel
    ↓
Background Service Worker
    ↓
Content Script
    ↓
YouTube <video>
    ↓
Set currentTime
```

This lets the user jump directly to the relevant part of the video.

---

# Tech Stack

## Frontend / Chrome Extension

* React
* Vite
* JavaScript
* Chrome Extension Manifest V3
* Chrome Side Panel API
* React Markdown
* Lucide React

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

## AI / RAG

* LangChain
* Google Gemini
* Gemini Embeddings
* Retrieval-Augmented Generation (RAG)

## Vector Search

* FAISS

## Transcript

* `youtube-transcript-api`

---

# Project Structure

```text
VideoMind-AI/
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── routes/
│   │   │   └── video.py
│   │   │
│   │   └── services/
│   │       ├── transcript.py
│   │       ├── chunker.py
│   │       ├── embedding.py
│   │       ├── vector_store.py
│   │       └── rag.py
│   │
│   ├── .env
│   ├── requirements.txt
│   └── venv/
│
└── extension/
    │
    ├── public/
    │   ├── manifest.json
    │   ├── background.js
    │   └── content.js
    │
    ├── src/
    │   ├── App.jsx
    │   ├── App.css
    │   └── ...
    │
    ├── package.json
    └── vite.config.js
```

---

# API Endpoints

## Analyze Video

```http
POST /api/v1/video/analyze
```

Request:

```json
{
  "videoId": "VIDEO_ID"
}
```

Response:

```json
{
  "success": true,
  "videoId": "VIDEO_ID",
  "totalChunks": 10,
  "message": "Video analyzed successfully"
}
```

---

## Ask a Question

```http
POST /api/v1/video/chat
```

Request:

```json
{
  "videoId": "VIDEO_ID",
  "question": "What is vibe coding?"
}
```

Response:

```json
{
  "success": true,
  "videoId": "VIDEO_ID",
  "question": "What is vibe coding?",
  "answer": "Vibe coding is...",
  "sources": [
    {
      "start_time": 35.2,
      "end_time": 58.7
    }
  ]
}
```

---

# Local Setup

## Prerequisites

Make sure you have:

* Python 3.10+
* Node.js
* npm
* Google Gemini API key
* Google Chrome

---

# Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Extension Setup

Navigate to the extension:

```bash
cd extension
```

Install dependencies:

```bash
npm install
```

Build the extension:

```bash
node .\node_modules\vite\bin\vite.js build
```

This creates the production build inside:

```text
extension/dist/
```

---

# Load Extension in Chrome

1. Open Chrome.
2. Navigate to:

```text
chrome://extensions/
```

3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the generated:

```text
extension/dist
```

folder.
6. Open a YouTube video.
7. Open the VideoMind side panel.
8. Wait for the video to become ready.
9. Ask a question.

---

# Environment Variables

The backend requires:

```env
GEMINI_API_KEY=your_api_key
```

Never commit the `.env` file.

Recommended `.gitignore`:

```gitignore
.env
venv/
__pycache__/
node_modules/
dist/
```

---

# RAG Pipeline

The complete pipeline can be summarized as:

```text
YouTube Video
      ↓
Video ID
      ↓
Transcript
      ↓
Timestamp-aware Chunks
      ↓
Gemini Embeddings
      ↓
FAISS Vector Store
      ↓
Similarity Retrieval
      ↓
Relevant Transcript Context
      ↓
Gemini LLM
      ↓
Grounded Answer
      ↓
Answer + Timestamp Sources
```

This project was intentionally built to understand the individual components of a RAG system rather than treating RAG as a single abstraction.

---

# Current Limitations

### In-Memory Vector Store

FAISS is currently stored in application memory.

```text
Server restart
     ↓
Vector store is cleared
```

Persistent vector storage has not been implemented yet.

### API Quotas

The project uses Gemini APIs, so available model and embedding quotas depend on the configured Google AI account and model tier.

### Transcript Availability

The system depends on a usable YouTube transcript. Videos without an accessible transcript may not be analyzable.

### Local Backend

The current extension communicates with:

```text
http://127.0.0.1:8000
```

so the current setup is primarily intended for local development.

---

# Future Improvements

Potential future versions can include:

* Persistent FAISS indexes
* Cloud deployment
* Authentication
* Better transcript chunking
* Improved retrieval strategies
* Hybrid search
* Reranking
* Conversation-aware questions
* Better source previews
* Video summaries
* Automatic key-point extraction
* Multi-language transcript support
* Streaming AI responses
* Better loading and error states
* Chrome Web Store release

---



