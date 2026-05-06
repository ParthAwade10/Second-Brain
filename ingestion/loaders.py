import fitz  # pymupdf
from pathlib import Path


def load_pdf(path: str) -> list[dict]:
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({
                "text": text,
                "metadata": {
                    "source": path,
                    "page": i + 1,
                    "type": "pdf"
                }
            })
    doc.close()
    return pages


def load_markdown(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [{
        "text": text,
        "metadata": {
            "source": path,
            "page": 1,
            "type": "markdown"
        }
    }]


def load_file(path: str) -> list[dict]:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return load_pdf(path)
    elif ext in [".md", ".txt"]:
        return load_markdown(path)
    else:
        print(f"Unsupported file type: {ext}")
        return []


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_docs/test_note.md"
    pages = load_file(path)
    print(f"Loaded {len(pages)} page(s) from '{path}'")
    for i, p in enumerate(pages):
        print(f"  Page {i+1}: {len(p['text'])} chars | metadata: {p['metadata']}")