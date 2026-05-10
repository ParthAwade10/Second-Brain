from typing import Generator

from config import CLAUDE_MODEL, client
from retrieval.dense import dense_search
from retrieval.fusion import rrf_fusion
from retrieval.reranker import rerank
from retrieval.sparse import sparse_search

SYSTEM_PROMPT = """You are Second Brain — an expert AI study assistant and personal tutor with access to the user's personal notes, documents, and study materials.

Your role:
- Answer questions thoroughly, using the provided source material as your primary basis
- Create detailed, well-structured study guides with clear sections, key concepts, definitions, and summary points
- Explain complex concepts with examples and helpful analogies
- Connect ideas across different documents in the knowledge base
- Help with exam prep, concept clarification, problem-solving, and deep understanding

Response guidelines:
- Use markdown — headers, bullet points, bold key terms, code blocks where relevant
- Be comprehensive but well-organized; structure makes content scannable
- Ground answers in the provided sources; cite [Source N] when drawing from specific material
- If sources don't contain enough to answer, say so clearly and offer what context you can
- For study guides: open with a brief overview, break into logical sections, close with summary/key takeaways"""


def retrieve(query: str) -> list[dict]:
    dense = dense_search(query)
    sparse = sparse_search(query)
    fused = rrf_fusion(dense, sparse)
    return rerank(query, fused)


def stream_answer(question: str, mode: str, chunks: list[dict]) -> Generator[str, None, None]:
    if not chunks:
        yield "I don't have any documents in your knowledge base yet. Please upload some notes or PDFs first."
        return

    context = "\n\n".join(
        f"[Source {i + 1} | {c['metadata'].get('source', 'unknown')}]\n{c['text']}"
        for i, c in enumerate(chunks)
    )

    mode_prefix = (
        "Create a comprehensive, well-structured study guide for the following question or topic."
        if mode == "guide"
        else "Answer the following question thoroughly and clearly."
    )

    # System prompt is cached — saves tokens on every subsequent call
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[
            {
                "role": "user",
                "content": f"{mode_prefix}\n\nSources:\n{context}\n\nQuestion: {question}",
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            yield text


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "What is self-attention?"
    mode = sys.argv[2] if len(sys.argv) > 2 else "qa"
    print(f"Query: {query}\nMode: {mode}\n{'─' * 60}")
    chunks = retrieve(query)
    print(f"Retrieved {len(chunks)} chunks\n{'─' * 60}\n")
    for token in stream_answer(query, mode, chunks):
        print(token, end="", flush=True)
    print()
