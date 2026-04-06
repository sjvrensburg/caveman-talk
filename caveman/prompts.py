"""Prompt constants for caveman compression and decompression."""

COMPRESS_SYSTEM = (
    "You are an expert at caveman compression. "
    "Always compress the provided text, never ask for clarification."
)

COMPRESS_USER_TEMPLATE = """\
Aggressively remove all stop words and grammatical scaffolding while \
preserving meaning. Output ONLY the compressed text, nothing else.

ALWAYS REMOVE:
- Articles: a, an, the
- Auxiliary verbs: is, are, was, were, am, be, been, being, have, has, had, \
do, does, did
- Common prepositions when meaning stays clear: of, for, to, in, on, at
- Pronouns when context is clear: it, this, that, these, those
- Pure intensifiers: very, quite, rather, somewhat, really, extremely
- Filler words: just, basically, actually, simply, essentially
- Pleasantries: sure, certainly, of course, happy to

ALWAYS KEEP:
- All nouns (people, places, things, concepts)
- All main verbs (actions, not auxiliaries)
- All adjectives that add meaning
- All numbers and quantifiers
- Negations (not, no, never, without)
- Uncertainty qualifiers (appears, seems, might, likely)
- Time/frequency words (daily, always, never, every Tuesday)
- Names, titles, technical terms
- Critical prepositions that change meaning (from, with, without)

BE SMART ABOUT:
- Keep prepositions when they define relationships: "made from wood" (keep)
- Remove "is/are/was/were" unless passive voice matters
- One thought per fragment, 2-5 words each
- Use short synonyms: big not extensive, fix not "implement a solution for"

TEXT TO COMPRESS:
{text}"""

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
