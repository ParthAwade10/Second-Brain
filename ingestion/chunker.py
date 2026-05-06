# FIXED-SIZE Character Chunking w/ Overlap

# Chunk 0: |-------- 512 chars --------|
# Chunk 1:                     |-------- 512 chars --------|
#                          ↑
#                     50 char overlap

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


if __name__ == "__main__":
    import sys
    from ingestion.loaders import load_file

    # FIXED-SIZE Character Chunking w/ Overlap

    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_docs/test_note.md"
    pages = load_file(path)
    chunks = chunk_documents(pages)
    print(f"Produced {len(chunks)} chunk(s) from '{path}'")
    for c in chunks:
        preview = c["text"][:80].replace("\n", " ")
        print(f"  [{c['metadata']['chunk_index']}] {len(c['text'])} chars | {preview}...")