"""
CampusHelp - Phase 4: Answer Generation (Google GenAI / Gemini version)
----------------------------------------------------------------------
Takes the chunks returned by retrieve.py plus the original question, sends
them to Gemini with a strict "answer only from context" instruction, and
returns a grounded answer. Falls back to a safe "I don't know" response if
no relevant chunks were found — this is what prevents hallucination.

Requires GOOGLE_API_KEY set in a .env file at the project root.
Get a free key at: https://aistudio.google.com/apikey

Usage (standalone test):
    python generate.py "What is the minimum attendance required?"
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from .retrieve import retrieve

# ---------- Config ----------
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

MODEL_NAME = "gemini-3.6-flash"
MAX_TOKENS = 500

FALLBACK_MESSAGE = (
    "I don't have this information in the available documents. "
    "Please check with the administration office."
)

SYSTEM_PROMPT = (
    "You are CampusHelp, a college helpdesk assistant. Answer the user's "
    "question using ONLY the context provided below. Do not use outside "
    "knowledge, do not guess, and do not make anything up. "
    "If the context does not contain enough information to answer the "
    "question, say exactly: "
    f'"{FALLBACK_MESSAGE}"'
)


# ---------- Client (lazy singleton) ----------
_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY not found. Add it to your .env file."
            )
        _client = genai.Client(api_key=api_key)
    return _client


# ---------- Prompt construction ----------
def build_context_block(matches: list[dict]) -> str:
    """Format retrieved chunks into a labeled context block for the prompt."""
    blocks = []
    for i, m in enumerate(matches, 1):
        blocks.append(f"[Source {i}: {m['source']}]\n{m['text']}")
    return "\n\n".join(blocks)


def build_user_message(question: str, context: str) -> str:
    return (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above."
    )


# ---------- LLM call ----------
def call_llm(question: str, context: str) -> str:
    client = get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=build_user_message(question, context),
        config={
            "system_instruction": SYSTEM_PROMPT,
            "max_output_tokens": MAX_TOKENS,
        },
    )
    return response.text.strip()


# ---------- Main generation function ----------
def generate_answer(question: str) -> dict:
    """
    Full generate step: retrieve relevant chunks, then call the LLM.
    Returns a dict: {"answer": ..., "sources": [...], "grounded": bool}

    "grounded" is False when no relevant chunks were found at all — in that
    case we skip the LLM call entirely and return the fallback directly,
    rather than risk the model inventing an answer from weak context.
    """
    matches = retrieve(question)

    if not matches:
        return {
            "answer": FALLBACK_MESSAGE,
            "sources": [],
            "grounded": False,
        }

    context = build_context_block(matches)
    answer = call_llm(question, context)

    sources = sorted({m["source"] for m in matches})

    return {
        "answer": answer,
        "sources": sources,
        "grounded": True,
    }


# ---------- Standalone test ----------
if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "What is the minimum attendance required to sit for exams?"
    print(f"Query: {query}\n")

    result = generate_answer(query)

    print(f"Answer: {result['answer']}\n")
    if result["sources"]:
        print(f"Sources: {', '.join(result['sources'])}")
    else:
        print("Sources: none (fallback triggered)")