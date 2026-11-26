"""HTTP API and web UI."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import audio
from .config import Settings
from .filenames import content_disposition, download_name
from .jobs import JobRunner
from .library import Library
from .providers import ProviderError, VoiceProvider, configured_providers

STATIC = Path(__file__).parent / "static"
MEDIA_TYPES = {"mp3": "audio/mpeg", "wav": "audio/wav"}


class NarrationRequest(BaseModel):
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)  # no maximum: long stories are split and joined back together
    provider: str
    voice: str = Field(min_length=1)
    model: str = ""


def create_app(settings: Settings | None = None,
               providers: dict[str, VoiceProvider] | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    providers = configured_providers(settings) if providers is None else providers
    library = Library(settings.data_dir)
    runner = JobRunner(settings, library, providers)

    @asynccontextmanager
    async def lifespan(_app):
        yield
        runner.shutdown()

    app = FastAPI(title="Story Narrator", lifespan=lifespan)
    app.state.library, app.state.runner = library, runner

    def _get(nid: str) -> dict:
        rec = library.get(nid)
        if rec is None:
            raise HTTPException(404, "Narration not found")
        return rec

    @app.get("/api/status")
    def status():
        return {
            "ffmpeg": audio.ffmpeg_available(),
            "providers": [{"id": p.name, "label": p.label, "models": p.models,
                           "default_model": p.default_model, "chunk_chars": p.chunk_chars}
                          for p in providers.values()],
        }

    @app.get("/api/providers/{name}/voices")
    def voices(name: str):
        p = providers.get(name)
        if p is None:
            raise HTTPException(404, "Provider not configured")
        try:
            return {"voices": p.voices()}
        except (ProviderError, OSError) as e:
            return {"voices": [], "error": str(e)}

    @app.post("/api/narrations", status_code=202)
    def create(req: NarrationRequest):
        p = providers.get(req.provider)
        if p is None:
            raise HTTPException(400, f"Voice provider '{req.provider}' is not configured.")
        if not audio.ffmpeg_available():
            raise HTTPException(503, "ffmpeg is not installed on the server; it is needed to export MP3.")
        rec = library.create(req.title.strip(), req.text, p.name, req.voice.strip(),
                             req.model.strip() or p.default_model)
        runner.submit(rec["id"])
        return rec

    @app.get("/api/narrations")
    def list_narrations(q: str = ""):
        return {"narrations": library.list(q.strip())}

    @app.get("/api/narrations/{nid}")
    def get_narration(nid: str, text: bool = False):
        rec = library.get(nid, with_text=text)
        if rec is None:
            raise HTTPException(404, "Narration not found")
        return rec

    @app.post("/api/narrations/{nid}/retry", status_code=202)
    def retry(nid: str):
        rec = _get(nid)
        if rec["status"] in ("queued", "generating"):
            raise HTTPException(409, "This narration is already being generated.")
        library.update(nid, status="queued", error=None, chunks_done=0, finished_at=None)
        runner.submit(nid)
        return library.get(nid)

    @app.delete("/api/narrations/{nid}", status_code=204)
    def delete(nid: str):
        if not library.delete(nid):
            raise HTTPException(404, "Narration not found")

    @app.get("/api/narrations/{nid}/audio.{ext}")
    def audio_file(nid: str, ext: str, download: bool = Query(False)):
        if ext not in MEDIA_TYPES:
            raise HTTPException(404, "Unknown format")
        rec = _get(nid)
        path = library.file_for(nid, ext)
        if rec["status"] != "ready" or not rec[f"has_{ext}"] or not path.is_file():
            raise HTTPException(404, f"{ext.upper()} is not available for this narration.")
        name = download_name(rec["title"], rec["created_at"], ext)
        # FileResponse streams from disk and supports Range, so long files are never truncated.
        return FileResponse(path, media_type=MEDIA_TYPES[ext],
                            headers={"Content-Disposition": content_disposition(name, download)})

    app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
    return app
