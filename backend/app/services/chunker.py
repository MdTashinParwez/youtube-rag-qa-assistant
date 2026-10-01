from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def create_chunks(transcript_data):

    documents = []

    current_text = []
    chunk_start = None
    chunk_end = None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Build timestamp-aware text blocks
    for item in transcript_data:

        if chunk_start is None:
            chunk_start = item["start"]

        current_text.append(item["text"])

        chunk_end = item["start"] + item["duration"]

        current_text_text = " ".join(current_text)

        if len(current_text_text) >= 1000:

            documents.append(
                Document(
                    page_content=current_text_text,
                    metadata={
                        "start_time": chunk_start,
                        "end_time": chunk_end
                    }
                )
            )

            # Keep overlap
            overlap_text = current_text_text[-200:]

            current_text = [overlap_text]
            chunk_start = chunk_end

    # Remaining text
    if current_text:
        documents.append(
            Document(
                page_content=" ".join(current_text),
                metadata={
                    "start_time": chunk_start,
                    "end_time": chunk_end
                }
            )
        )

    return documents