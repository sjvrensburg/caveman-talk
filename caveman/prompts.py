"""Prompt constants for caveman compression and decompression."""

COMPRESS_SYSTEM = (
    "You are an expert at caveman compression. "
    "Always compress the provided text, never ask for clarification."
)

_COMPRESS_BASE = """\
Strip grammatical scaffolding, preserve meaning. Output ONLY compressed text.

REMOVE: articles (a/an/the), auxiliaries (is/are/was/were/have/has/do/does), \
clear-context pronouns (it/this/that), filler (just/basically/actually/simply), \
intensifiers (very/quite/really/extremely), pleasantries, redundant prepositions.

KEEP: nouns, main verbs, meaningful adjectives, numbers, negations, \
uncertainty qualifiers (might/likely), time words, names, technical terms, \
meaning-changing prepositions (from/with/without)."""

_INTENSITY_SUFFIX = {
    "lite": """
STYLE: Drop filler and hedging. Keep articles and full sentences. Professional but tight.""",
    "full": """
STYLE: 2-5 word fragments. Short synonyms (big not extensive, fix not \
"implement a solution for"). One thought per fragment.""",
    "ultra": """
STYLE: Maximum compression. Abbreviate common terms (DB/auth/config/req/res/fn/impl/dep/env/repo/dir). \
Arrows for causality (X -> Y). Single words when possible.""",
}

INTENSITIES = tuple(_INTENSITY_SUFFIX.keys())


def compress_user_prompt(text: str, intensity: str = "full") -> str:
    """Build the compress user prompt for the given intensity."""
    suffix = _INTENSITY_SUFFIX[intensity]
    return f"{_COMPRESS_BASE}{suffix}\n\nTEXT TO COMPRESS:\n{text}"


# Default template kept for backwards compatibility with existing callers.
COMPRESS_USER_TEMPLATE = (
    _COMPRESS_BASE + _INTENSITY_SUFFIX["full"] + "\n\nTEXT TO COMPRESS:\n{text}"
)

DECOMPRESS_SYSTEM = (
    "You are a language expansion expert. "
    "Convert caveman-compressed text back into proper, fluent English "
    "while preserving ALL semantic information."
)

DECOMPRESS_USER_TEMPLATE = """\
The input uses caveman compression:
- Very short fragments (2-5 words)
- No articles or connectives
- Active voice, concrete language
- Minimal grammatical scaffolding

Your task:
1. Expand to natural English sentences
2. Add appropriate connectives (because, therefore, however)
3. Add articles (a, an, the) where natural
4. Ensure smooth flow between sentences
5. Maintain ALL facts, constraints, and logical steps
6. Use proper grammar and style

Output ONLY the expanded English text, nothing else.

CAVEMAN TEXT TO EXPAND:
{text}"""
