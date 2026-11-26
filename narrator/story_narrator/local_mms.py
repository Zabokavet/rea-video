"""Native Haitian Creole voice: Meta's MMS-TTS model (facebook/mms-tts-hat), run on this computer.

It is an AI voice model trained on Haitian Creole speech. It runs locally on the CPU, so it
is free and has no usage limits. The model (about 145 MB) downloads the first time it is
used. Its licence is CC-BY-NC-4.0: fine for personal use, not for commercial use.

Optional dependencies: pip install -e '.[kreyol]'  (torch + transformers)
"""
from __future__ import annotations

import importlib.util
import re
import threading
import unicodedata
import zlib

from .chunking import _CLAUSE_END, _SENTENCE_END, _pieces
from .config import Settings
from .languages import LANGUAGES, language as lang_info
from .providers import Audio, ProviderError, VoiceProvider

SENTENCE_PAUSE = 0.40  # seconds of silence after each sentence (the model ignores punctuation)
CLAUSE_PAUSE = 0.15    # after commas, semicolons, colons
_KEEP_ACCENTS = {"à", "è", "ò"}  # the only accented letters in Kreyòl spelling


def mms_installed() -> bool:
    return all(importlib.util.find_spec(m) for m in ("torch", "transformers"))


def fold_for_model(text: str, vocab: set[str]) -> str:
    """Lowercase and map letters the model can't read to ones it can (é→e, ç→s, ’→')."""
    out = []
    for ch in unicodedata.normalize("NFC", text.lower().replace("’", "'").replace("‘", "'")):
        if ch in vocab or ch.isspace():
            out.append(ch)
        elif ch == "ç":
            out.append("s")
        elif ch not in _KEEP_ACCENTS:
            base = unicodedata.normalize("NFD", ch)[0]
            out.append(base if base in vocab else " ")
    return re.sub(r"\s+", " ", "".join(out)).strip()


class MMSProvider(VoiceProvider):
    def __init__(self, s: Settings):
        super().__init__(
            name="mms", label="Meta MMS · Kreyòl (lokal, gratis)", chunk_chars=600,
            models=["mms-tts"], default_model="mms-tts",
            languages={code: "native" for code, info in LANGUAGES.items() if info.get("mms")},
            note="Runs on this computer: free and unlimited. First use downloads the voice (~145 MB).")
        self._cache_dir = s.hf_cache_dir or None
        self._models: dict[str, tuple] = {}
        self._load_lock = threading.Lock()
        self._run_lock = threading.Lock()

    def voices(self) -> list[dict]:
        return [{"id": "default", "name": "Vwa MMS"}]

    def _model(self, checkpoint: str):
        with self._load_lock:
            if checkpoint not in self._models:
                if not mms_installed():
                    raise ProviderError("The local Creole voice needs torch and transformers: "
                                        "pip install -e '.[kreyol]'")
                from transformers import AutoTokenizer, VitsModel
                try:
                    tok = AutoTokenizer.from_pretrained(checkpoint, cache_dir=self._cache_dir)
                    model = VitsModel.from_pretrained(checkpoint, cache_dir=self._cache_dir).eval()
                except OSError as e:
                    raise ProviderError(f"Couldn't download the voice model {checkpoint}: {e}") from e
                self._models[checkpoint] = (tok, model, set(tok.get_vocab()))
            return self._models[checkpoint]

    def synthesize(self, text, voice, model, lossless, language="ht"):
        import numpy as np
        import torch

        checkpoint = lang_info(language).get("mms")
        if not checkpoint:
            raise ProviderError(f"No local voice for language '{language}'.")
        tok, vits, vocab = self._model(checkpoint)
        rate = vits.config.sampling_rate
        out: list = []
        for sentence in _pieces(text, _SENTENCE_END):
            clauses = _pieces(sentence, _CLAUSE_END)
            for j, clause in enumerate(clauses):
                cleaned = fold_for_model(clause, vocab)
                if not re.search(r"\w", cleaned):
                    continue
                inputs = tok(cleaned, return_tensors="pt")
                if inputs.input_ids.shape[-1] == 0:
                    continue
                with self._run_lock, torch.no_grad():
                    # The model's rhythm is random; seed it from the text so output is repeatable.
                    torch.manual_seed(zlib.crc32(cleaned.encode()))
                    wav = vits(**inputs).waveform[0].cpu().numpy()
                out.append(wav)
                pause = SENTENCE_PAUSE if j == len(clauses) - 1 else CLAUSE_PAUSE
                out.append(np.zeros(int(rate * pause), dtype=wav.dtype))
        if not out:
            out.append(np.zeros(int(rate * SENTENCE_PAUSE), dtype="float32"))
        pcm = (np.clip(np.concatenate(out), -1.0, 1.0) * 32767).astype("<i2").tobytes()
        return Audio(pcm, "pcm", rate)
