# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

caveman-talk is a plugin for Claude Code and Codex that provides two forms of token-saving "caveman compression":

1. **Response-side skill** (`skills/caveman-talk/SKILL.md`) — pure prompt engineering, no runtime cost. Makes the agent respond in terse caveman-speak at three intensity levels (lite/full/ultra). Activated via `/caveman-talk:caveman [intensity]`.
2. **Input-side CLI tools** (`caveman-compress`, `caveman-decompress`) — Python package that sends text through an OpenAI-compatible `/v1/chat/completions` endpoint using tuned system prompts for compression/decompression.

## Build & Install

```bash
pip install -e ".[dev]"   # editable install with pytest
```

## Testing

```bash
python -m pytest tests/ -v        # run all tests
python -m pytest tests/ -k test_caching  # run single test by name
```

## Architecture

- `caveman/prompts.py` — System and user prompt templates for compress/decompress; `compress_user_prompt()` builds intensity-specific prompts
- `caveman/translate.py` — `compress()` and `decompress()` functions that call `_chat()`, plus CLI entry points (`_cli_compress`, `_cli_decompress`)
- `caveman/__init__.py` — Re-exports `compress` and `decompress`
- `bin/` — Standalone scripts (legacy path-hacking wrappers; the pip-installed entry points in `pyproject.toml` are the canonical CLI)
- `skills/caveman-talk/SKILL.md` — The skill prompt file, discovered by Claude Code from `.claude/skills/` directories
- `.claude-plugin/plugin.json` — Claude Code plugin manifest
- `.codex-plugin/plugin.json` — Codex plugin manifest (references `skills/` for skill discovery)

## Environment Variables (for CLI tools)

| Variable | Default | Required |
|----------|---------|----------|
| `CAVEMAN_API_KEY` | — | Yes |
| `CAVEMAN_API_BASE` | `https://api.openai.com/v1` | No |
| `CAVEMAN_MODEL` | `gpt-4o-mini` | No |
| `CAVEMAN_TIMEOUT` | `60` | No |

## Key Design Decisions

- The skill is a single Markdown file with no code dependencies — it works via prompt injection into the agent's context.
- CLI tools use `requests` directly (no OpenAI SDK) to stay minimal and work with any compatible endpoint.
- `bin/` scripts exist for environments where pip install isn't available; `pyproject.toml` `[project.scripts]` is the primary CLI mechanism.
