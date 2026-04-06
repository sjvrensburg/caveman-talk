# caveman-talk

You're a caveman. Claude's a caveman. We all save tokens.

A plugin for Claude Code and Codex that combines two forms of caveman compression:

- **Response-side**: A skill that makes Claude respond in terse caveman-speak (lite/full/ultra intensity)
- **Input-side**: CLI tools that compress/decompress text via any OpenAI-compatible API endpoint

## Installation

### Skill only (response-side caveman)

The skill is a single `SKILL.md` file — pure prompt engineering, no Python needed. Claude Code discovers skills from `.claude/skills/` directories:

```bash
# Clone the repo
git clone https://github.com/sjvrensburg/caveman-talk.git

# Install into your project (skill available when working in that project)
mkdir -p /path/to/your-project/.claude/skills/caveman-talk
cp caveman-talk/skills/caveman-talk/SKILL.md /path/to/your-project/.claude/skills/caveman-talk/

# Or install globally (available in all projects)
mkdir -p ~/.claude/skills/caveman-talk
cp caveman-talk/skills/caveman-talk/SKILL.md ~/.claude/skills/caveman-talk/
```

This gives you the `/caveman-talk:caveman` skill inside Claude Code.

### CLI tools (input-side compression)

The CLI tools (`caveman-compress` and `caveman-decompress`) require Python. Install via pip:

```bash
pip install -e /path/to/caveman-talk
```

This installs both commands and their Python dependencies. You can use the CLI tools with or without the skill.

### As a Codex plugin

```bash
# Install from a local clone
codex plugin add /path/to/caveman-talk
```

This gives you the `/caveman-talk:caveman` skill inside Codex. Note: Codex does not auto-add `bin/` to PATH, so install the CLI tools via pip (above) if you need them.

### Requirements

- Python 3.9+
- `requests` (installed automatically via pip; already available in most environments)

## Configuration

The CLI tools call an OpenAI-compatible chat completions endpoint. Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CAVEMAN_API_KEY` | *(required)* | API key for the endpoint |
| `CAVEMAN_API_BASE` | `https://api.openai.com/v1` | Base URL for the API |
| `CAVEMAN_MODEL` | `gpt-4o-mini` | Model to use for translation |

Any provider that exposes `/v1/chat/completions` works — OpenAI, Ollama, LM Studio, vLLM, Together, Groq, etc.

### Provider examples

```bash
# OpenAI
export CAVEMAN_API_KEY="sk-..."

# Ollama (local, free)
export CAVEMAN_API_BASE="http://localhost:11434/v1"
export CAVEMAN_API_KEY="ollama"
export CAVEMAN_MODEL="llama3"

# LM Studio (local, free)
export CAVEMAN_API_BASE="http://localhost:1234/v1"
export CAVEMAN_API_KEY="lm-studio"
export CAVEMAN_MODEL="local-model"

# Groq (fast, free tier available)
export CAVEMAN_API_BASE="https://api.groq.com/openai/v1"
export CAVEMAN_API_KEY="gsk_..."
export CAVEMAN_MODEL="llama-3.3-70b-versatile"
```

## Usage

### Skill — make the agent respond in caveman

Activate inside Claude Code or Codex:

```
/caveman-talk:caveman          # default (full) intensity
/caveman-talk:caveman lite     # mild terseness
/caveman-talk:caveman full     # classic caveman
/caveman-talk:caveman ultra    # maximum compression
```

#### Intensity levels

| Level | What it does | Example |
|-------|-------------|---------|
| **lite** | Drops filler and hedging, keeps articles and full sentences | "The issue is in the auth middleware. The token expiry check uses `<` instead of `<=`." |
| **full** | Drops articles, fragments OK, short synonyms | "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:" |
| **ultra** | Abbreviations, arrows for causality, maximum compression | "auth middleware bug. expiry: `<` -> `<=`. fix:" |

#### A note on thinking tokens

The caveman skill compresses **output tokens only** — the visible response text. It cannot affect the model's internal thinking/reasoning traces, which often account for the majority of token usage. This is an architectural limitation: skills are prompt-injected into the assistant context and only shape generated output, not internal chain-of-thought.

Caveman compression becomes proportionally more impactful when thinking is short — for example, when using low thinking effort or a reduced `budget_tokens` setting. Pairing `/caveman-talk:caveman ultra` with low thinking effort gives the best overall token savings.

The **CLI tools** (input-side compression) complement the skill by reducing input token counts, which the skill cannot do.

#### Safety

Caveman mode automatically suspends for:
- Security warnings and vulnerability disclosures
- Irreversible action confirmations (destructive git ops, DB drops)
- Code blocks, git commits, and error messages (always written normally)

Say "stop caveman" or "normal mode" to turn it off.

### CLI tools — compress and decompress text

```bash
# Compress via stdin
echo "The system should validate all user inputs before processing them" | caveman-compress
# → Validate user inputs before processing

# Compress via argument
caveman-compress "Please ensure that the database connection is properly configured"
# → Configure database connection before running migration scripts

# Decompress
echo "Validate user inputs before processing" | caveman-decompress
# → You should validate the user inputs before processing them.
```

The tools preserve numbers, names, technical terms, and code through the round-trip. SQL, JSON, and other structured content passes through largely unchanged.

## How it works

The **skill** (response-side) is pure prompt engineering — a `SKILL.md` file that instructs the agent (Claude or Codex) to drop grammatical fluff from its responses. No API calls, no runtime cost.

The **CLI tools** (input-side) send text to an OpenAI-compatible `/v1/chat/completions` endpoint with carefully tuned system prompts for compression and decompression. The prompts instruct the model to strip articles, auxiliary verbs, filler words, and unnecessary prepositions while preserving all semantic content.

## Credits

This project combines ideas from two open-source projects:

- **[wilpel/caveman-compression](https://github.com/wilpel/caveman-compression)** — Lossless semantic compression for LLM contexts. Pioneered the approach of using LLM-based, NLP-based, and MLM-based methods to strip grammatical scaffolding from text while preserving meaning. The compression and decompression prompts in caveman-talk are adapted from this project's prompt design and formal specification (SPEC.md).

- **[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)** — A Claude Code skill that makes Claude respond in terse caveman-speak. Introduced the intensity levels (lite/full/ultra), auto-clarity suspension for safety-critical output, and the elegant single-file SKILL.md packaging. The skill prompt in caveman-talk builds on this project's design.

## License

MIT
