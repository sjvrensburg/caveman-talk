# caveman-talk

You're a caveman. Claude's a caveman. We all save tokens.

A Claude Code plugin that combines two forms of caveman compression:

- **Response-side**: A skill that makes Claude respond in terse caveman-speak (lite/full/ultra intensity)
- **Input-side**: CLI tools that compress/decompress text via any OpenAI-compatible API endpoint

## Install as Claude Code plugin

```bash
claude plugin add /path/to/caveman-talk
```

## Configuration

The CLI tools need an OpenAI-compatible endpoint. Set these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CAVEMAN_API_KEY` | *(required)* | API key for the endpoint |
| `CAVEMAN_API_BASE` | `https://api.openai.com/v1` | Base URL (works with OpenAI, Ollama, LM Studio, vLLM, etc.) |
| `CAVEMAN_MODEL` | `gpt-4o-mini` | Model to use for compression |

### Examples for different providers

```bash
# OpenAI
export CAVEMAN_API_KEY="sk-..."

# Ollama (local)
export CAVEMAN_API_BASE="http://localhost:11434/v1"
export CAVEMAN_API_KEY="ollama"
export CAVEMAN_MODEL="llama3"

# LM Studio (local)
export CAVEMAN_API_BASE="http://localhost:1234/v1"
export CAVEMAN_API_KEY="lm-studio"
export CAVEMAN_MODEL="local-model"
```

## Usage

### Skill (response-side)

In Claude Code, activate caveman responses:

```
/caveman-talk:caveman          # default (full) intensity
/caveman-talk:caveman lite     # mild — no filler, but keeps articles
/caveman-talk:caveman full     # classic caveman fragments
/caveman-talk:caveman ultra    # maximum compression, abbreviations, arrows
```

Say "stop caveman" or "normal mode" to revert.

### CLI tools (input-side)

```bash
# Compress text
echo "The system should validate all user inputs before processing them" | caveman-compress
# → system validate user inputs before processing

# Decompress back
echo "system validate user inputs before processing" | caveman-decompress
# → The system should validate all user inputs before processing them.

# Or pass as argument
caveman-compress "Please ensure that the database connection is properly configured"
```

### Install CLI tools via pip (optional)

```bash
pip install -e /path/to/caveman-talk
```

This makes `caveman-compress` and `caveman-decompress` available globally.

## Credits

Combines ideas from:
- [wilpel/caveman-compression](https://github.com/wilpel/caveman-compression) — prompt compression via LLM/NLP
- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — caveman-speak skill for Claude Code
