"""Core compress/decompress functions using any OpenAI-compatible API."""

import os
import sys
from typing import Callable, Optional, Tuple

import requests

from .prompts import (
    COMPRESS_SYSTEM,
    COMPRESS_USER_TEMPLATE,
    DECOMPRESS_SYSTEM,
    DECOMPRESS_USER_TEMPLATE,
    INTENSITIES,
    compress_user_prompt,
)

_cached_config: Optional[Tuple[str, str, str, int]] = None


def _get_config() -> Tuple[str, str, str, int]:
    global _cached_config
    if _cached_config is not None:
        return _cached_config
    api_base = os.environ.get("CAVEMAN_API_BASE", "https://api.openai.com/v1")
    api_key = os.environ.get("CAVEMAN_API_KEY")
    if not api_key:
        print("Error: CAVEMAN_API_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)
    model = os.environ.get("CAVEMAN_MODEL", "gpt-4o-mini")
    timeout = int(os.environ.get("CAVEMAN_TIMEOUT", "60"))
    _cached_config = (api_base.rstrip("/"), api_key, model, timeout)
    return _cached_config


def _chat(system: str, user: str) -> str:
    api_base, api_key, model, timeout = _get_config()
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
        timeout=timeout,
    )
    if not resp.ok:
        try:
            detail = resp.json()
        except (ValueError, KeyError):
            detail = resp.text
        raise RuntimeError(
            f"API request failed ({resp.status_code}): {detail}"
        )
    return resp.json()["choices"][0]["message"]["content"].strip()


def compress(text: str, intensity: str = "full") -> str:
    """Compress text to caveman-speak via an OpenAI-compatible API."""
    return _chat(COMPRESS_SYSTEM, compress_user_prompt(text, intensity))


def decompress(text: str) -> str:
    """Decompress caveman-speak back to fluent English."""
    return _chat(DECOMPRESS_SYSTEM, DECOMPRESS_USER_TEMPLATE.format(text=text))


def _parse_compress_args() -> Tuple[str, str]:
    """Parse CLI args for compress, returning (text, intensity)."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="caveman-compress",
        description="Compress text to caveman-speak",
    )
    parser.add_argument(
        "-i", "--intensity",
        choices=INTENSITIES,
        default="full",
        help="compression intensity (default: full)",
    )
    parser.add_argument("text", nargs="*", help="text to compress")
    args = parser.parse_args()

    if args.text:
        text = " ".join(args.text)
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_usage(sys.stderr)
        sys.exit(1)

    return text.strip(), args.intensity


def _cli_compress() -> None:
    text, intensity = _parse_compress_args()
    if not text:
        sys.exit(0)
    try:
        print(compress(text, intensity))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _cli_decompress() -> None:
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Usage: caveman-decompress <text>", file=sys.stderr)
        print("       echo <text> | caveman-decompress", file=sys.stderr)
        sys.exit(1)
    text = text.strip()
    if not text:
        sys.exit(0)
    try:
        print(decompress(text))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
