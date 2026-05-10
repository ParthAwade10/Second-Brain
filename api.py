import json
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from qdrant_client import QdrantClient

from agents.agent import retrieve, stream_answer
from config import COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT
from ingestion.chunker import chunk_documents
from ingestion.embedder import embed_and_store
from ingestion.loaders import load_file

app = FastAPI(title="Second Brain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory document registry (resets on server restart — fine for local dev)
_docs: list[dict] = []


class QueryRequest(BaseModel):
    question: str
    mode: str = "qa"  # "qa" | "guide"


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        try:
            pages = load_file(tmp_path)
            if not pages:
                results.append({"name": file.filename, "status": "error", "message": "Could not parse file"})
                continue
            chunks = chunk_documents(pages)
            embed_and_store(chunks)
            entry = {"name": file.filename, "chunks": len(chunks), "type": suffix.lstrip(".")}
            _docs.append(entry)
            results.append({"name": file.filename, "status": "ok", "chunks": len(chunks)})
        except Exception as e:
            results.append({"name": file.filename, "status": "error", "message": str(e)})
        finally:
            os.unlink(tmp_path)
    return {"results": results}


@app.post("/api/query")
async def query(req: QueryRequest):
    async def generate():
        try:
            chunks = retrieve(req.question)
            sources = [
                {"text": c["text"][:400], "metadata": c["metadata"]}
                for c in chunks
            ]
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
            for token in stream_answer(req.question, req.mode, chunks):
                yield f"data: {json.dumps({'type': 'text', 'content': token})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/documents")
async def list_documents():
    return {"documents": _docs}


@app.delete("/api/documents")
async def clear_documents():
    qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    try:
        qdrant.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _docs.clear()
    return {"status": "cleared"}


# Serve frontend — must come last so API routes take priority
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
