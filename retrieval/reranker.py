from config import TOP_K_RERANK


def rerank(query: str, results: list[dict], top_k: int = TOP_K_RERANK) -> list[dict]:
    if not results:
        return []
    try:
        from flashrank import Ranker, RerankRequest
        ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/tmp/flashrank")
        passages = [{"id": i, "text": r["text"]} for i, r in enumerate(results)]
        reranked = ranker.rerank(RerankRequest(query=query, passages=passages))
        return [{**results[r["id"]], "rerank_score": r["score"]} for r in reranked[:top_k]]
    except Exception:
        # Graceful fallback — return top_k by RRF score
        return results[:top_k]


if __name__ == "__main__":
    import sys
    from retrieval.dense import dense_search
    from retrieval.sparse import sparse_search
    from retrieval.fusion import rrf_fusion

    query = sys.argv[1] if len(sys.argv) > 1 else "transformer attention mechanism"
    fused = rrf_fusion(dense_search(query), sparse_search(query))
    final = rerank(query, fused)
    print(f"Reranked results for '{query}': {len(final)}")
    for r in final:
        print(f"  {r['text'][:80]}...")
