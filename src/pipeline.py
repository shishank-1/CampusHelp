"""
CampusHelp - Pipeline
-------------------------
Wires ingest -> embed -> retrieve -> generate into a small set of simple,
callable functions. app.py should only ever talk to this file — it should
never need to import ingest.py, embed.py, retrieve.py, or generate.py
directly. This keeps the UI layer decoupled from internal implementation.

Exposed functions:
    ask_question(question)        -> for the User flow
    upload_and_process(file_path) -> for the Admin flow
"""

from pathlib import Path
import shutil

from .ingest import process_document, RAW_DOCS_DIR
from .embed import (
    load_embedding_model,
    get_chroma_collection,
    clear_source_from_collection,
)
from .generate import generate_answer


# =====================================================================
# USER FLOW: question -> grounded answer
# =====================================================================
def ask_question(question: str) -> dict:
    """
    Single entry point for the User flow.

    Returns:
        {
            "answer": str,
            "sources": list[str],
            "grounded": bool
        }
    """
    if not question or not question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": [],
            "grounded": False,
        }

    return generate_answer(question.strip())


# =====================================================================
# ADMIN FLOW: new file -> ingested, embedded, searchable
# =====================================================================
def upload_and_process(uploaded_file_path: Path, original_filename: str | None = None) -> dict:
    """
    Single entry point for the Admin flow. Takes the path to a file that has
    already been saved somewhere (e.g. a temp path from Streamlit's file
    uploader), copies it into data/raw_docs/, then runs ingest + embed on
    that single file only (not the whole folder) so uploads stay fast.

    Returns:
        {
            "success": bool,
            "filename": str,
            "num_chunks": int,
            "message": str
        }
    """
    uploaded_file_path = Path(uploaded_file_path)
    filename = original_filename or uploaded_file_path.name
    suffix = uploaded_file_path.suffix.lower()

    if suffix not in (".pdf", ".docx"):
        return {
            "success": False,
            "filename": filename,
            "num_chunks": 0,
            "message": f"Unsupported file type: {suffix}. Only PDF and DOCX are allowed.",
        }

    # 1. Copy the file into data/raw_docs/ (this becomes the permanent copy)
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = RAW_DOCS_DIR / filename
    shutil.copy(uploaded_file_path, dest_path)

    # 2. Ingest: extract text + chunk (single file, not the whole folder)
    try:
        record = process_document(dest_path)
    except Exception as e:
        return {
            "success": False,
            "filename": filename,
            "num_chunks": 0,
            "message": f"Failed to process file: {e}",
        }

    # 3. Embed: convert this file's chunks to vectors and store them,
    #    clearing any older chunks from a previous upload of the same name
    model = load_embedding_model()
    collection = get_chroma_collection()
    clear_source_from_collection(collection, filename)

    chunks = record["chunks"]
    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]

    embeddings = model.encode(texts).tolist()
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    return {
        "success": True,
        "filename": filename,
        "num_chunks": len(chunks),
        "message": f"'{filename}' processed and added to the knowledge base "
                   f"({len(chunks)} chunks). No restart needed.",
    }