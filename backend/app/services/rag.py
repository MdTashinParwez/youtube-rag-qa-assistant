from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


def create_retriever(vector_store):

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 4
        }
    )

    return retriever


def create_llm():

    return ChatGoogleGenerativeAI(
        model="gemini-3.8-flash"
    )


prompt = PromptTemplate.from_template("""
You are a YouTube video Q&A assistant.

Your job is to answer the user's question using ONLY the provided
transcript context.

Rules:
1. Answer the question directly.
2. Do not mention "the transcript" or "the context" unless necessary.
3. Do not add information that is not supported by the context.
4. If the context does not contain enough information, say:
   "I couldn't find enough information about that in the video."
5. Keep the answer concise but informative.
6. When explaining a concept, separate:
   - What it is
   - Why it matters
7. Preserve important technical terms exactly as they appear.

Transcript context:
{context}

User question:
{question}

Answer:
""")


def generate_answer(relevant_docs, question):

    context = "\n\n".join(
        doc.page_content
        for doc in relevant_docs
    )

    llm = create_llm()

    final_prompt = prompt.format(
        context=context,
        question=question
    )

    response = llm.invoke(final_prompt)

    if isinstance(response.content, list):
        return "".join(
            item.get("text", "")
            for item in response.content
            if isinstance(item, dict)
        )

    return response.content