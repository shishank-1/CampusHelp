"""
CampusHelp - Phase 3: Retrieval
-----------------------------------
Takes a user's natural-language question, converts it into a vector using
the same embedding model used in embed.py, and searches ChromaDB for the
most semantically similar stored chunks.

Usage (standalone test):
    python retrieve.py "What is the minimum attendance required?"
"""

import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# ---------- Config ----------
VECTORSTORE_DIR = Path(__file__).parent.parent / "vectorstore" / "chroma_db"
COLLECTION_NAME = "campushelp_docs"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # must match embed.py exactly

TOP_K = 3                    # how many chunks to retrieve
MIN_SIMILARITY = 0.35        # below this, we treat the match as "not relevant"
                              # (tune this after testing on real queries)


# ---------- Lazy-loaded singletons ----------
# Loading the model and DB connection is slow, so we cache them at module
# level and reuse across calls instead of reloading on every question.
_model = None
_collection = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def get_collection():
    global _collection
    if _collection is None:
        if not VECTORSTORE_DIR.exists():
            raise FileNotFoundError(
                f"No vector store found at {VECTORSTORE_DIR}. "
                "Run ingest.py and embed.py first."
            )
        client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
        _collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


# ---------- Similarity helper ----------
def distance_to_similarity(distance: float) -> float:
    """
    ChromaDB's default distance metric is cosine distance (0 = identical,
    2 = opposite). Convert to a 0-1 similarity score that's easier to reason
    about and threshold against.
    """
    return max(0.0, 1.0 - (distance / 2.0))


# ---------- Main retrieval function ----------
def retrieve(question: str, top_k: int = TOP_K, min_similarity: float = MIN_SIMILARITY) -> list[dict]:
    """
    Given a user question, return the top_k most relevant chunks as a list of
    dicts: {"text": ..., "source": ..., "similarity": ...}

    Chunks below `min_similarity` are filtered out — if the result is an
    empty list, generate.py should treat that as "no relevant context found"
    and return the safe fallback answer instead of guessing.
    """
    if not question or not question.strip():
        return []

    model = get_embedding_model()
    collection = get_collection()

    query_embedding = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    matches = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        if not doc or dist is None:
            continue

        similarity = distance_to_similarity(dist)
        if similarity >= min_similarity:
            matches.append({
                "text": doc,
                "source": (meta or {}).get("source", "unknown"),
                "similarity": round(similarity, 3),
            })

    return matches


# ---------- Standalone test ----------
if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "What is the minimum attendance required to sit for exams?"
    print(f"Query: {query}\n")

    matches = retrieve(query)

    if not matches:
        print("No relevant chunks found above similarity threshold.")
    else:
        for i, m in enumerate(matches, 1):
            print(f"[{i}] source={m['source']} similarity={m['similarity']}")
            print(f"    {m['text'][:200]}...\n")