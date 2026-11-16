"""Small shared helpers: logging, ffmpeg wrappers, hashing, fonts."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

STUDIO_HOME = Path(os.environ.get("REA_STUDIO_HOME", Path.home() / ".rea-studio"))
PKG_DIR = Path(__file__).resolve().parent

_VERBOSE = os.environ.get("REA_STUDIO_VERBOSE") == "1"


def log(msg: str) -> None:
    print(f"[studio] {msg}", file=sys.stderr, flush=True)


def debug(msg: str) -> None:
    if _VERBOSE:
        log(msg)


def which(name: str) -> str | None:
    return shutil.which(name)


def run(cmd: list[str], *, quiet: bool = True, check: bool = True, input: bytes | None = None) -> subprocess.CompletedProcess:
    debug("$ " + " ".join(str(c) for c in cmd))
    p = subprocess.run([str(c) for c in cmd], input=input, capture_output=True)
    if check and p.returncode != 0:
        err = p.stderr.decode(errors="replace")[-3000:]
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(str(c) for c in cmd)[:400]}\n{err}")
    if not quiet:
        sys.stderr.write(p.stderr.decode(errors="replace"))
    return p


def ffmpeg(*args: str | Path) -> None:
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args])


def probe_duration(path: str | Path) -> float:
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path])
    return float(json.loads(p.stdout)["format"]["duration"])


def probe_streams(path: str | Path) -> dict:
    p = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    return json.loads(p.stdout)


def stable_hash(*parts) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(json.dumps(p, sort_keys=True, ensure_ascii=False, default=str).encode())
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- fonts
# Ordered by preference per role. The installer drops OFL fonts into STUDIO_HOME/fonts;
# otherwise we fall back to common system fonts.
_FONT_CANDIDATES = {
    "title": ["Anton-Regular.ttf", "BebasNeue-Regular.ttf", "Montserrat-Black.ttf", "Inter-Black.ttf",
              "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"],
    "serif": ["PlayfairDisplay-Bold.ttf", "PlayfairDisplay[wght].ttf", "DejaVuSerif-Bold.ttf",
              "LiberationSerif-Bold.ttf", "Georgia Bold.ttf", "georgiab.ttf"],
    "body": ["Montserrat-SemiBold.ttf", "Montserrat-Bold.ttf", "Inter-SemiBold.ttf", "Inter-Bold.ttf",
             "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"],
}
_FONT_DIRS = [STUDIO_HOME / "fonts", PKG_DIR / "data" / "fonts", Path("/usr/share/fonts"),
              Path("/usr/local/share/fonts"), Path.home() / ".fonts", Path.home() / ".local/share/fonts",
              Path("/Library/Fonts"), Path("/System/Library/Fonts"), Path.home() / "Library/Fonts",
              Path("C:/Windows/Fonts")]
_font_index: dict[str, Path] | None = None


def _index_fonts() -> dict[str, Path]:
    global _font_index
    if _font_index is None:
        _font_index = {}
        for d in _FONT_DIRS:
            if d.is_dir():
                for f in d.rglob("*"):
                    if f.suffix.lower() in (".ttf", ".otf"):
                        _font_index.setdefault(f.name.lower(), f)
    return _font_index


def find_font(role: str = "body") -> Path | None:
    idx = _index_fonts()
    for name in _FONT_CANDIDATES.get(role, _FONT_CANDIDATES["body"]):
        if name.lower() in idx:
            return idx[name.lower()]
    # anything at all
    return next(iter(idx.values()), None)


def font_dirs_for_libass() -> list[Path]:
    return [d for d in _FONT_DIRS if d.is_dir()]


def font_family(path: Path | None) -> str:
    """Best-effort family name for ASS styles (libass matches on family)."""
    if path is None:
        return "Sans"
    try:
        from PIL import ImageFont
        return ImageFont.truetype(str(path), 20).getname()[0]
    except Exception:
        return path.stem.split("-")[0]
