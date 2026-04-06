"""Caveman compression — translate text to/from caveman-speak."""

from .prompts import INTENSITIES
from .translate import compress, decompress

__all__ = ["compress", "decompress", "INTENSITIES"]
