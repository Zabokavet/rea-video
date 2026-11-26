# Story Narrator

Turn a written story into an AI-narrated audio file. Listen to it in the browser, download it as MP3 or WAV, and find every past narration in the audio library.

You don't record anything: every narration is synthesized by the AI voice provider you connect (OpenAI TTS or ElevenLabs).

> This app is self-contained and separate from rea-video. It lives in this folder for now; you can move it to its own repository unchanged.

## Features

| | |
|---|---|
| **Downloads** | A **Download Audio (MP3)** button after every successful generation, plus **Download WAV** when the provider supplies lossless audio. |
| **Preview player** | Play, pause, resume, replay, jump ±10 s, seek, and set speed from 0.5× to 2× without changing pitch. The speed setting is remembered. Space toggles play/pause. |
| **Filenames** | Named after the story title plus the date and time it was created, e.g. `The-Lighthouse-Keeper_2026-11-26_1405.mp3`. Non-Latin titles are kept for modern browsers (`filename*`), with an ASCII fallback. |
| **Quality** | The app asks the provider for raw PCM and saves it unchanged as the WAV master. The MP3 is encoded once from that master at LAME's best VBR setting. If your plan only allows MP3, the provider's MP3 frames are joined with stream copy and never re-encoded. |
| **Long stories** | No length cap. Text is split at paragraph, then sentence, then clause boundaries to fit the provider's per-request limit, and the parts are joined into one file. Files are streamed from disk with HTTP Range support, so long narrations download and seek in full. |
| **Audio library** | Every narration is listed with date, length, voice and formats. Each entry has its own Play, MP3 and WAV buttons, plus Retry (for failed ones) and Delete. You can search by title or text. |
| **No app-imposed limits** | No quotas, character caps or daily limits. Several narrations can generate at once (`NARRATOR_WORKERS`); extra ones wait in a queue instead of being refused. The only limits are your provider's own rate limits and pricing: HTTP 429 and transient errors are retried with backoff, honouring `Retry-After`. |

## Run it

Needs Python 3.10+ and ffmpeg (`brew install ffmpeg` / `sudo apt install ffmpeg`).

```bash
cd narrator
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
cp .env.example .env        # add OPENAI_API_KEY and/or ELEVENLABS_API_KEY
story-narrator              # http://127.0.0.1:8000
```

Options: `story-narrator --env-file path/to/.env --host 0.0.0.0 --port 8000`. All settings are listed in [`.env.example`](.env.example).

Narrations are stored under `data/` (`NARRATOR_DATA_DIR`): a SQLite library and one folder of audio per narration.

There is no login. The app is meant for personal use on your own machine. Don't expose it to the internet as-is: anyone who can reach it could spend your provider credit.

## Provider notes

- **OpenAI** returns 24 kHz PCM, so you always get both WAV and MP3. Each request takes up to 4,000 characters; longer stories are split automatically.
- **ElevenLabs** voices are loaded from your account; you can also paste a voice ID. `pcm_24000` works on every plan. Set `ELEVENLABS_PCM_FORMAT=pcm_44100` on Pro or higher. If your plan refuses PCM, the app falls back to MP3 and that narration has no WAV.

## API

| Method | Path | |
|---|---|---|
| GET | `/api/status` | configured providers, ffmpeg check |
| GET | `/api/providers/{id}/voices` | voices for a provider |
| POST | `/api/narrations` | `{title, text, provider, voice, model?}` → starts a job (202) |
| GET | `/api/narrations?q=` | the library |
| GET | `/api/narrations/{id}` | status and progress (`chunks_done` / `chunks_total`) |
| POST | `/api/narrations/{id}/retry` | regenerate a failed narration |
| DELETE | `/api/narrations/{id}` | remove it and its files |
| GET | `/api/narrations/{id}/audio.mp3` · `audio.wav` | stream inline; add `?download=1` to save as a file |

## Tests

```bash
pip install -e '.[dev]' && python -m pytest -q
```

The tests use a fake voice provider and a mocked HTTP transport, so they need no API keys and make no network calls.
