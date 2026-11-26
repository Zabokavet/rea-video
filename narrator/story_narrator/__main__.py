"""Run the Story Narrator server: python -m story_narrator [--env-file .env] [--host] [--port]"""
from __future__ import annotations

import argparse


def main() -> None:
    ap = argparse.ArgumentParser(prog="story-narrator")
    ap.add_argument("--env-file", default=".env", help="file with API keys (default: .env)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    from .config import load_env_file
    load_env_file(args.env_file)

    import uvicorn
    from .app import create_app
    uvicorn.run(create_app(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
