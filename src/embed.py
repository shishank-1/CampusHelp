"""
CampusHelp - Phase 2: Embedding & Vector Storage
--------------------------------------------------
Reads the chunked text produced by ingest.py (data/processed/chunks.json),
converts each chunk into a vector embedding, and stores it in a persistent
ChromaDB collection along with its original text and source metadata.

Usage:
    python embed.py                # embeds everything in chunks.json
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# ---------- Config ----------
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
CHUNKS_FILE = PROCESSED_DIR / "chunks.json"

VECTORSTORE_DIR = Path(__file__).parent.parent / "vectorstore" / "chroma_db"
COLLECTION_NAME = "campushelp_docs"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, good enough for short docs


# ---------- Load chunks ----------
def load_chunks() -> list[dict]:
    """Load all chunk records produced by ingest.py."""
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"{CHUNKS_FILE} not found. Run ingest.py first to generate it."
        )
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    # Flatten: each record has a list of chunks under record["chunks"]
    all_chunks = []
    for record in records:
        all_chunks.extend(record["chunks"])
    return all_chunks


# ---------- Embedding model ----------
def load_embedding_model() -> SentenceTransformer:
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


# ---------- ChromaDB setup ----------
def get_chroma_collection():
    """Return a persistent ChromaDB collection, creating it if needed."""
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def clear_source_from_collection(collection, source_file: str):
    """
    Remove any existing chunks belonging to a given source file before
    re-adding it. Prevents duplicate chunks when a document is re-ingested.
    """
    existing = collection.get(where={"source": source_file})
    if existing and existing.get("ids"):
        collection.delete(ids=existing["ids"])
        print(f"  -> Cleared {len(existing['ids'])} old chunk(s) for {source_file}")


# ---------- Main embedding pipeline ----------
def run_embedding():
    chunks = load_chunks()
    if not chunks:
        print("No chunks found. Nothing to embed.")
        return

    model = load_embedding_model()
    collection = get_chroma_collection()

    # A full embedding run mirrors chunks.json, so remove stale documents too.
    existing = collection.get()
    if existing and existing.get("ids"):
        collection.delete(ids=existing["ids"])
        print(f"  -> Cleared {len(existing['ids'])} existing chunk(s)")

    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]

    print(f"Embedding {len(texts)} chunk(s)...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"\nDone. {len(texts)} chunk(s) embedded and stored in:")
    print(f"  {VECTORSTORE_DIR}")
    print(f"Collection '{COLLECTION_NAME}' now has {collection.count()} total chunk(s).")


if __name__ == "__main__":
    run_embedding()