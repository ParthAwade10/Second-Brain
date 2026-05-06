import uuid

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, EMBEDDING_MODEL

VECTOR_DIM = 384  # all-MiniLM-L6-v2 output dimension


def _get_client() -> QdrantClient:
    return QdrantClient(host="localhost", port=6333)


def _ensure_collection(client: QdrantClient) -> None:
    existing = {c.name for c in client.get_collections().collections}
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )


def embed_and_store(chunks: list[dict]) -> None:
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [chunk["text"] for chunk in chunks]
    vectors = model.encode(texts, show_progress_bar=True).tolist()

    client = _get_client()
    _ensure_collection(client)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": chunk["text"], **chunk["metadata"]},
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(points)} chunks in '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    import sys
    from ingestion.loaders import load_file
    from ingestion.chunker import chunk_documents

    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_docs/test_note.md"
    pages = load_file(path)
    chunks = chunk_documents(pages)
    print(f"Embedding {len(chunks)} chunk(s) from '{path}'...")
    embed_and_store(chunks)

    client = _get_client()
    count = client.count(collection_name=COLLECTION_NAME).count
    print(f"Collection '{COLLECTION_NAME}' now has {count} point(s).")
