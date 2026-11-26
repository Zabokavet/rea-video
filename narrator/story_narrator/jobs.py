"""Background narration jobs: chunk the story, synthesize every chunk, assemble the files."""
from __future__ import annotations

import logging
import shutil
from concurrent.futures import ThreadPoolExecutor

from . import audio
from .chunking import split_text
from .config import Settings
from .library import Library, now
from .providers import Audio, ProviderError, VoiceProvider

log = logging.getLogger("story_narrator")

# Status codes that mean "this output format isn't offered to you", not "your request is bad".
_FORMAT_REFUSALS = {400, 402, 403, 422}


class JobRunner:
    def __init__(self, settings: Settings, library: Library, providers: dict[str, VoiceProvider]):
        self.settings, self.library, self.providers = settings, library, providers
        # A queue, not a cap: extra jobs wait their turn instead of being refused.
        self._pool = ThreadPoolExecutor(max_workers=settings.workers, thread_name_prefix="narrate")

    def submit(self, nid: str) -> None:
        self._pool.submit(self._run_safely, nid)

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)

    def _run_safely(self, nid: str) -> None:
        try:
            self.run(nid)
        except Exception as e:  # report any failure on the record instead of losing it
            log.exception("narration %s failed", nid)
            self.library.update(nid, status="failed", error=str(e) or e.__class__.__name__, finished_at=now())

    def run(self, nid: str) -> None:
        rec = self.library.get(nid, with_text=True)
        provider = self.providers.get(rec["provider"])
        if provider is None:
            raise ProviderError(f"Voice provider '{rec['provider']}' is not configured (missing API key).")

        chunks = split_text(rec["text"], provider.chunk_chars)
        if not chunks:
            raise ValueError("The story text is empty.")
        self.library.update(nid, status="generating", chunks_total=len(chunks), chunks_done=0, error=None)

        lossless = True
        parts: list[Audio] = []
        for i, text in enumerate(chunks):
            parts.append(self._synthesize(provider, text, rec, lossless))
            if parts[-1].kind == "mp3" and lossless:
                lossless = False
                if parts[:-1]:  # PCM already fetched for earlier chunks; formats must match
                    raise ProviderError("The provider stopped returning lossless audio mid-narration; please retry.")
            self.library.update(nid, chunks_done=i + 1)

        out_dir = self.library.dir_for(nid)
        tmp_dir = out_dir.with_name(out_dir.name + ".part")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        tmp_dir.mkdir(parents=True)
        try:
            wav, mp3 = tmp_dir / "narration.wav", tmp_dir / "narration.mp3"
            if lossless:
                rate = parts[0].sample_rate
                duration = audio.write_wav([p.data for p in parts], wav, rate, parts[0].channels)
                audio.encode_mp3(wav, mp3, self.settings.mp3_vbr_quality)
                fields = dict(has_wav=True, has_mp3=True, sample_rate=rate, duration=duration)
            else:
                audio.concat_mp3([p.data for p in parts], mp3)
                fields = dict(has_wav=False, has_mp3=True, sample_rate=None, duration=audio.probe_duration(mp3))
            shutil.rmtree(out_dir, ignore_errors=True)
            tmp_dir.rename(out_dir)
        except BaseException:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise
        if self.library.get(nid) is None:  # deleted from the library while it was generating
            shutil.rmtree(out_dir, ignore_errors=True)
            return
        self.library.update(nid, status="ready", finished_at=now(), **fields)

    @staticmethod
    def _synthesize(provider: VoiceProvider, text: str, rec: dict, lossless: bool) -> Audio:
        if not lossless:
            return provider.synthesize(text, rec["voice"], rec["model"], lossless=False)
        try:
            return provider.synthesize(text, rec["voice"], rec["model"], lossless=True)
        except ProviderError as e:
            if e.status not in _FORMAT_REFUSALS:
                raise
            # The plan may not include PCM. Try MP3; if that fails too, the original error stands.
            try:
                return provider.synthesize(text, rec["voice"], rec["model"], lossless=False)
            except ProviderError:
                raise e from None
