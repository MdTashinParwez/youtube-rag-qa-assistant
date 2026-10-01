from langchain_community.vectorstores import FAISS

from app.services.embedding import create_embeddings


# Temporary in-memory cache
vector_stores = {}


def create_vector_store(chunks):

    embeddings = create_embeddings()

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_store


def get_or_create_vector_store(video_id, chunks):

    # Already indexed
    if video_id in vector_stores:
        return vector_stores[video_id]

    # First time indexing
    vector_store = create_vector_store(chunks)

    # Save in memory
    vector_stores[video_id] = vector_store

    return vector_store