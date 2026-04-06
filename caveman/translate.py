"""Core compress/decompress functions using any OpenAI-compatible API."""

import os
import sys

import requests

from .prompts import (
    COMPRESS_SYSTEM,
    COMPRESS_USER_TEMPLATE,
    DECOMPRESS_SYSTEM,
    DECOMPRESS_USER_TEMPLATE,
)


def _get_config():
    api_base = os.environ.get("CAVEMAN_API_BASE", "https://api.openai.com/v1")
    api_key = os.environ.get("CAVEMAN_API_KEY")
    if not api_key:
        print("Error: CAVEMAN_API_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)
    model = os.environ.get("CAVEMAN_MODEL", "gpt-4o-mini")
    return api_base.rstrip("/"), api_key, model


def _chat(system: str, user: str) -> str:
    api_base, api_key, model = _get_config()
    resp = requests.post(
        f"{api_base}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def compress(text: str) -> str:
    """Compress text to caveman-speak via an OpenAI-compatible API."""
    return _chat(COMPRESS_SYSTEM, COMPRESS_USER_TEMPLATE.format(text=text))


def decompress(text: str) -> str:
    """Decompress caveman-speak back to fluent English."""
    return _chat(DECOMPRESS_SYSTEM, DECOMPRESS_USER_TEMPLATE.format(text=text))


def _cli_main(fn):
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        name = "caveman-compress" if fn is compress else "caveman-decompress"
        print(f"Usage: {name} <text>", file=sys.stderr)
        print(f"       echo <text> | {name}", file=sys.stderr)
        sys.exit(1)
    text = text.strip()
    if not text:
        sys.exit(0)
    try:
        print(fn(text))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _cli_compress():
    _cli_main(compress)


def _cli_decompress():
    _cli_main(decompress)
