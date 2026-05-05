def chunk_documents(pages: list[dict]) -> list[dict]:
    chunks = []
    for page in pages:
        text = page["text"]
        chunk_size = 512
        overlap = 50
        start = 0
        i = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        **page["metadata"],
                        "chunk_index": i
                    }
                })
            start = end - overlap
            i += 1
    return chunks