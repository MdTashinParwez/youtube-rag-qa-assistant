import os
import time

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()


def create_embeddings():
    api_key = os.getenv("GEMINI_API_KEY")

    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        api_key=api_key
    )


def embed_documents_with_retry(texts, batch_size=50):

    embeddings = create_embeddings()

    all_embeddings = []

    for i in range(0, len(texts), batch_size):

        batch = texts[i:i + batch_size]

        for attempt in range(3):

            try:
                batch_embeddings = embeddings.embed_documents(batch)

                all_embeddings.extend(batch_embeddings)

                break

            except Exception as e:

                if "429" not in str(e):
                    raise

                if attempt == 2:
                    raise

                time.sleep(10)

    return all_embeddings