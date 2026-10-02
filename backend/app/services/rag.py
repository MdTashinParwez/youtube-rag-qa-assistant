# from langchain_core.prompts import PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI


# def create_retriever(vector_store):

#     retriever = vector_store.as_retriever(
#         search_type="similarity",
#         search_kwargs={
#             "k": 4
#         }
#     )

#     return retriever


# def create_llm():

#     return ChatGoogleGenerativeAI(
#         model="gemini-3.8-flash"
#     )


# prompt = PromptTemplate.from_template("""
# You are a YouTube video Q&A assistant.

# Your job is to answer the user's question using ONLY the provided
# transcript context.

# Rules:
# 1. Answer the question directly.
# 2. Do not mention "the transcript" or "the context" unless necessary.
# 3. Do not add information that is not supported by the context.
# 4. If the context does not contain enough information, say:
#    "I couldn't find enough information about that in the video."
# 5. Keep the answer concise but informative.
# 6. When explaining a concept, separate:
#    - What it is
#    - Why it matters
# 7. Preserve important technical terms exactly as they appear.

# Transcript context:
# {context}

# User question:
# {question}

# Answer:
# """)


# def generate_answer(relevant_docs, question):

#     context = "\n\n".join(
#         doc.page_content
#         for doc in relevant_docs
#     )

#     llm = create_llm()

#     final_prompt = prompt.format(
#         context=context,
#         question=question
#     )

#     response = llm.invoke(final_prompt)

#     if isinstance(response.content, list):
#         return "".join(
#             item.get("text", "")
#             for item in response.content
#             if isinstance(item, dict)
#         )

#     return response.content

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
        model="gemini-3.8-flash",
        temperature=0.2
    )


prompt = PromptTemplate.from_template("""
You are an intelligent YouTube video Q&A assistant.

Your task is to answer the user's question based ONLY on the
provided video transcript excerpts.

IMPORTANT:
The transcript is SOURCE MATERIAL, not the answer itself.
Do NOT simply repeat, copy, or paraphrase the transcript.
First understand what the user is asking, then synthesize the
relevant information into a useful answer.

Follow these rules carefully:

1. Answer the user's EXACT question.
   Do not give unrelated information from the video.

2. Use only information supported by the provided context.
   Do not invent facts or use outside knowledge.

3. Reason over the retrieved information.
   Combine relevant points when necessary instead of describing
   each transcript chunk separately.

4. If the user asks "what is X":
   - Give a clear definition.
   - Explain the idea in simple language.
   - Mention the relevant details from the video.

5. If the user asks "why is X important":
   - Explain the significance or impact described or supported
     by the video.
   - Do not merely repeat statements made in the transcript.

6. If the user asks "how":
   - Explain the process or mechanism step by step when the
     context contains enough information.

7. If the question asks for a comparison:
   - Clearly explain the relevant differences.
   - Do not introduce information that is absent from the context.

8. Do not start with phrases such as:
   "According to the transcript..."
   "The video says..."
   "The transcript mentions..."

9. Do not mention retrieved chunks, vector databases, RAG,
   embeddings, or internal system details.

10. Do not unnecessarily summarize the entire video when the
    user asks about one specific concept.

11. Prefer a natural answer with short paragraphs and bullets
    when they improve readability.

12. Keep the answer concise but intellectually useful.
    Explain the idea rather than just restating sentences.

13. If the provided context does not contain enough information
    to answer the question, respond exactly with:
    "I couldn't find enough information about that in the video."

VIDEO CONTEXT:
----------------
{context}
----------------

USER QUESTION:
{question}

Now think about the question first, identify the relevant
information from the context, and then provide the best
grounded answer.

ANSWER:
""")


def generate_answer(relevant_docs, question):

    context_parts = []

    for doc in relevant_docs:

        start_time = doc.metadata.get("start_time")
        end_time = doc.metadata.get("end_time")

        context_parts.append(
            f"[Video: {start_time}s - {end_time}s]\n"
            f"{doc.page_content}"
        )

    context = "\n\n".join(context_parts)

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