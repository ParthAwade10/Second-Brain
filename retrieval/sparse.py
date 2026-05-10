from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient

from config import COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, TOP_K_SPARSE


def sparse_search(query: str, top_k: int = TOP_K_SPARSE) -> list[dict]:
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    try:
        points, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10_000,
            with_payload=True,
            with_vectors=False,
        )
    except Exception:
        return []

    if not points:
        return []

    corpus = [p.payload.get("text", "") for p in points]
    bm25 = BM25Okapi([doc.lower().split() for doc in corpus])
    scores = bm25.get_scores(query.lower().split())

    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [
        {
            "id": str(points[i].id),
            "score": float(scores[i]),
            "text": points[i].payload.get("text", ""),
            "metadata": {k: v for k, v in points[i].payload.items() if k != "text"},
        }
        for i in top_indices
        if scores[i] > 0
    ]


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "transformer attention mechanism"
    results = sparse_search(query)
    print(f"Sparse search: '{query}' → {len(results)} result(s)")
    for r in results:
        print(f"  [{r['score']:.4f}] {r['text'][:80]}...")
