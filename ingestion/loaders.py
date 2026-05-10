import base64
import fitz  # pymupdf
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MEDIA_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif",
}


def load_pdf(path: str) -> list[dict]:
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({
                "text": text,
                "metadata": {"source": path, "page": i + 1, "type": "pdf"}
            })
    doc.close()
    return pages


def load_markdown(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [{"text": text, "metadata": {"source": path, "page": 1, "type": "markdown"}}]


def load_image(path: str) -> list[dict]:
    from config import CLAUDE_MODEL, client

    ext = Path(path).suffix.lower()
    media_type = MEDIA_TYPES.get(ext, "image/jpeg")

    with open(path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": image_data},
                },
                {
                    "type": "text",
                    "text": (
                        "Extract and transcribe all text, diagrams, equations, tables, and key "
                        "information from this image. Preserve structure and include all details. "
                        "Output only the extracted content — no commentary."
                    ),
                },
            ],
        }],
    )

    extracted = response.content[0].text.strip()
    if not extracted:
        return []
    return [{"text": extracted, "metadata": {"source": path, "page": 1, "type": "image"}}]


def load_file(path: str) -> list[dict]:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return load_pdf(path)
    elif ext in {".md", ".txt"}:
        return load_markdown(path)
    elif ext in IMAGE_EXTENSIONS:
        return load_image(path)
    else:
        print(f"Unsupported file type: {ext}")
        return []


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_docs/test_note.md"
    pages = load_file(path)
    print(f"Loaded {len(pages)} page(s) from '{path}'")
    for i, p in enumerate(pages):
        print(f"  Page {i + 1}: {len(p['text'])} chars | metadata: {p['metadata']}")
