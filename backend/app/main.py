"""HTTP API. Every endpoint is under /api; the built Vue app is served at /.

Errors never contain human-readable text: they return {"detail": {"code": ...}}
and the frontend translates the code into 繁體中文 or English.
"""

from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import PROJECT_ROOT, RuntimeSettings, load_settings
from .embed import create_embedder
from .llm import create_llm
from .rag.loaders import is_supported
from .rag.service import IngestError, RagService


@lru_cache
def get_service() -> RagService:
    settings = load_settings()
    return RagService(settings, create_embedder(settings), create_llm(settings))


app = FastAPI(title="mini-RAG")


def error(status: int, code: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code})


def safe_name(name: str | None) -> str:
    """Strip any directory parts so a filename can't escape uploads/."""
    clean = Path(name or "").name
    if not clean or clean.startswith("."):
        raise error(400, "invalid_filename")
    return clean


# --- status & settings -------------------------------------------------------


@app.get("/api/status")
def status(svc: RagService = Depends(get_service)):
    return {
        "llm": svc.llm.name,
        "llm_configured": svc.llm.configured,
        "embedder": svc.embedder.name,
        "needs_reindex": svc.needs_reindex,
        "documents": len(svc.list_documents()),
        "chunks": len(svc.store),
        "max_upload_mb": svc.settings.max_upload_mb,
    }


@app.get("/api/settings")
def get_settings(svc: RagService = Depends(get_service)):
    return asdict(svc.runtime)


class SettingsIn(BaseModel):
    chunk_size: int
    chunk_overlap: int
    top_k: int


@app.put("/api/settings")
def put_settings(body: SettingsIn, svc: RagService = Depends(get_service)):
    try:
        svc.update_runtime(RuntimeSettings(**body.model_dump()))
    except ValueError as e:
        raise error(422, str(e)) from None
    return asdict(svc.runtime)


# --- documents ---------------------------------------------------------------


@app.get("/api/documents")
def list_documents(svc: RagService = Depends(get_service)):
    return svc.list_documents()


@app.post("/api/documents")
def upload_documents(files: list[UploadFile], svc: RagService = Depends(get_service)):
    """Upload one or more files. Each file succeeds or fails independently."""
    max_bytes = svc.settings.max_upload_mb * 1024 * 1024
    results = []
    for file in files:
        name = Path(file.filename or "").name
        result: dict = {"doc_id": name, "ok": False}
        content = file.file.read(max_bytes + 1)
        if not name or name.startswith("."):
            result["error"] = "invalid_filename"
        elif not is_supported(name):
            result["error"] = "unsupported_file_type"
        elif len(content) > max_bytes:
            result["error"] = "file_too_large"
        else:
            try:
                result["chunks"] = svc.ingest(name, content)
                result["ok"] = True
            except IngestError as e:
                result["error"] = e.code
            except Exception:
                result["error"] = "load_failed"
        results.append(result)
    return results


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str, svc: RagService = Depends(get_service)):
    if not svc.delete(safe_name(doc_id)):
        raise error(404, "document_not_found")
    return {"ok": True}


@app.post("/api/reindex")
def reindex(svc: RagService = Depends(get_service)):
    return {"errors": svc.reindex(), "chunks": len(svc.store)}


# --- ask ---------------------------------------------------------------------


class AskIn(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)


@app.post("/api/ask")
def ask(body: AskIn, svc: RagService = Depends(get_service)):
    if svc.needs_reindex:
        raise error(409, "needs_reindex")
    result = svc.ask(body.question.strip(), body.top_k)
    return {
        "answer": result.answer,
        "llm_configured": result.llm_configured,
        "sources": [
            {
                "n": n,
                "doc_id": hit.chunk.doc_id,
                "chunk_index": hit.chunk.index,
                "score": round(hit.score, 4),
                "text": hit.chunk.text,
            }
            for n, hit in enumerate(result.hits, start=1)
        ],
        "messages": result.messages,
    }


# --- frontend ----------------------------------------------------------------

DIST = PROJECT_ROOT / "frontend" / "dist"

if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        file = DIST / path
        if path and file.is_file() and DIST in file.resolve().parents:
            return FileResponse(file)
        return FileResponse(DIST / "index.html")
