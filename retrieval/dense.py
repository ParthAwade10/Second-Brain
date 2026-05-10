from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

from config import COLLECTION_NAME, EMBEDDING_MODEL, QDRANT_HOST, QDRANT_PORT, TOP_K_DENSE

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def dense_search(query: str, top_k: int = TOP_K_DENSE) -> list[dict]:
    vector = _get_model().encode(query).tolist()
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    try:
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=top_k,
        )
    except Exception:
        return []
    return [
        {
            "id": str(r.id),
            "score": r.score,
            "text": r.payload.get("text", ""),
            "metadata": {k: v for k, v in r.payload.items() if k != "text"},
        }
        for r in results
    ]


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "transformer attention mechanism"
    results = dense_search(query)
    print(f"Dense search: '{query}' → {len(results)} result(s)")
    for r in results:
        print(f"  [{r['score']:.4f}] {r['text'][:80]}...")
