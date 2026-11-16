#!/usr/bin/env bash
# rea-studio installer: local AI video studio (Linux / macOS / WSL). Safe to re-run.
#
#   bash studio/install.sh                 # install CLI + engines, link skills
#   bash studio/install.sh --models core   # also pre-download the core models (~6 GB)
#   bash studio/install.sh --models full   # + AnimateDiff-Lightning, MusicGen (~9 GB)
#   PYTHON_BIN=python3.11 bash studio/install.sh
#
# No sudo is used. Missing system packages (ffmpeg, espeak-ng) are reported with the command to install them.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
HOME_DIR="${REA_STUDIO_HOME:-$HOME/.rea-studio}"
VENV="$HOME_DIR/venv"
MODELS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --models) MODELS="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!!\033[0m %s\n' "$*" >&2; }
mkdir -p "$HOME_DIR"

# ---------------------------------------------------------------- 1. inspect
say "Inspecting system"
OS="$(uname -s)"; ARCH="$(uname -m)"
echo "  OS: $OS $ARCH"
if command -v nvidia-smi >/dev/null 2>&1; then
  GPU="$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)"; ACC=cuda
elif [ "$OS" = Darwin ] && [ "$ARCH" = arm64 ]; then GPU="Apple Silicon (MPS)"; ACC=mps
else GPU="none"; ACC=cpu; fi
echo "  GPU: $GPU"
df -h "$HOME_DIR" | tail -1 | awk '{print "  free disk: "$4}'

missing=()
command -v ffmpeg >/dev/null 2>&1 || missing+=(ffmpeg)
command -v espeak-ng >/dev/null 2>&1 || missing+=(espeak-ng)
if [ ${#missing[@]} -gt 0 ]; then
  warn "missing system packages: ${missing[*]}"
  case "$OS" in
    Darwin) warn "  brew install ${missing[*]}" ;;
    Linux) warn "  sudo apt install ${missing[*]}   (Fedora: sudo dnf install ${missing[*]})" ;;
  esac
  if [[ " ${missing[*]} " == *" ffmpeg "* ]]; then echo "ffmpeg is required. Install it and re-run." >&2; exit 1; fi
  warn "espeak-ng is needed for Kokoro non-English voices and the eSpeak Kreyòl voice; continuing without it."
fi

# ---------------------------------------------------------------- 2. python
# Kokoro (best TTS) supports Python 3.10-3.12.
PY="${PYTHON_BIN:-}"
if [ -z "$PY" ]; then
  for c in python3.12 python3.11 python3.10 python3; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(not ((3,10) <= sys.version_info[:2] <= (3,12)))'; then PY="$c"; break; fi
  done
fi
USE_UV=0; command -v uv >/dev/null 2>&1 && USE_UV=1
if [ -z "$PY" ]; then
  if [ $USE_UV = 1 ]; then say "No Python 3.10-3.12 found; uv will provide 3.12"; PY="3.12"
  else echo "Need Python 3.10-3.12 (Kokoro TTS does not support 3.13 yet). Install python3.12 or uv (https://docs.astral.sh/uv/) and re-run." >&2; exit 1; fi
fi
say "Python: $PY"

if [ ! -x "$VENV/bin/python" ]; then
  say "Creating venv $VENV"
  if [ $USE_UV = 1 ]; then uv venv -p "$PY" "$VENV"; else "$PY" -m venv "$VENV"; fi
fi
pipi() { if [ $USE_UV = 1 ]; then uv pip install --python "$VENV/bin/python" "$@"; else "$VENV/bin/python" -m pip install "$@"; fi; }
[ $USE_UV = 1 ] || "$VENV/bin/python" -m pip install -q --upgrade pip

# ---------------------------------------------------------------- 3. torch for this hardware
if ! "$VENV/bin/python" -c "import torch" 2>/dev/null; then
  say "Installing PyTorch for $ACC"
  if [ "$ACC" = cpu ] && [ "$OS" = Linux ]; then pipi torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
  else pipi torch torchvision torchaudio; fi
fi

# ---------------------------------------------------------------- 4. studio + engines
say "Installing rea-studio and engines (Kokoro, Piper, MMS via transformers, diffusers, faster-whisper, Real-ESRGAN loader)"
pipi -e "$HERE[all]" spandrel
# spaCy English model used by Kokoro's English G2P (otherwise Kokoro tries to download it at runtime)
"$VENV/bin/python" -c "import en_core_web_sm" 2>/dev/null || \
  pipi "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"

mkdir -p "$HOME/.local/bin"
ln -sfn "$VENV/bin/rea-studio" "$HOME/.local/bin/rea-studio"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) warn "add ~/.local/bin to PATH (e.g. echo 'export PATH=\$HOME/.local/bin:\$PATH' >> ~/.bashrc)";; esac

# ---------------------------------------------------------------- 5. fonts (SIL Open Font License, from github.com/google/fonts)
FONTS="$HOME_DIR/fonts"; mkdir -p "$FONTS"
fetch_font() {
  local path="$1" name; name="$(basename "$path")"
  [ -s "$FONTS/$name" ] || curl -fsSL "https://raw.githubusercontent.com/google/fonts/main/ofl/$path" -o "$FONTS/$name" \
    || { rm -f "$FONTS/$name"; warn "font $name not downloaded (system fonts will be used)"; }
}
say "Fetching OFL fonts"
fetch_font "anton/Anton-Regular.ttf"
fetch_font "bebasneue/BebasNeue-Regular.ttf"
# (static fonts only: variable fonts render at their default weight in libass/Pillow)

# ---------------------------------------------------------------- 6. skills
say "Linking skills"
for d in "$HERE"/skills/*/; do
  n="$(basename "$d")"
  for target in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
    mkdir -p "$target"; ln -sfn "${d%/}" "$target/$n"
  done
done
echo "  linked $(ls -d "$HERE"/skills/*/ | wc -l) skills into ~/.claude/skills and ~/.agents/skills"

# ---------------------------------------------------------------- 7. optional model pre-download
if [ -n "$MODELS" ]; then
  say "Pre-downloading models ($MODELS)"
  MODELS="$MODELS" "$VENV/bin/python" - <<'PY'
import os
from huggingface_hub import hf_hub_download, snapshot_download
core = [("hexgrad/Kokoro-82M", None), ("Lykon/dreamshaper-8", ["*.json", "*.txt", "unet/diffusion_pytorch_model.safetensors",
        "vae/diffusion_pytorch_model.safetensors", "text_encoder/model.safetensors", "tokenizer/*"]),
        ("latent-consistency/lcm-lora-sdv1-5", None), ("facebook/mms-tts-hat", None),
        ("depth-anything/Depth-Anything-V2-Small-hf", None), ("Systran/faster-whisper-small", None)]
full = [("ByteDance/AnimateDiff-Lightning", ["animatediff_lightning_4step_diffusers.safetensors"]),
        ("facebook/musicgen-small", None)]
for repo, pat in core + (full if os.environ["MODELS"] == "full" else []):
    print("  ", repo, flush=True)
    snapshot_download(repo, allow_patterns=pat)
for v in ["fr/fr_FR/tom/medium/fr_FR-tom-medium", "en/en_US/ryan/high/en_US-ryan-high", "pt/pt_BR/faber/medium/pt_BR-faber-medium",
          "es/es_ES/davefx/medium/es_ES-davefx-medium"]:
    for ext in (".onnx", ".onnx.json"):
        hf_hub_download("rhasspy/piper-voices", v + ext)
PY
fi

say "Done. Try:  rea-studio doctor  &&  rea-studio selftest --quick"
