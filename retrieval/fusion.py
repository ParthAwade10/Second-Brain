def rrf_fusion(dense: list[dict], sparse: list[dict], k: int = 60) -> list[dict]:
    """Reciprocal Rank Fusion — combines dense and sparse ranked lists."""
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    for rank, doc in enumerate(dense):
        key = doc["text"]
        scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
        doc_map[key] = doc

    for rank, doc in enumerate(sparse):
        key = doc["text"]
        scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
        doc_map[key] = doc

    return [
        {"rrf_score": scores[key], **doc_map[key]}
        for key in sorted(scores, key=lambda x: scores[x], reverse=True)
    ]


if __name__ == "__main__":
    import sys
    from retrieval.dense import dense_search
    from retrieval.sparse import sparse_search

    query = sys.argv[1] if len(sys.argv) > 1 else "transformer attention mechanism"
    fused = rrf_fusion(dense_search(query), sparse_search(query))
    print(f"Fused results for '{query}': {len(fused)}")
    for r in fused[:5]:
        print(f"  [rrf={r['rrf_score']:.4f}] {r['text'][:80]}...")
