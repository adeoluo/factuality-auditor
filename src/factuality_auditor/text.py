"""Deterministic normalization and sentence splitting."""

from __future__ import annotations

import re

_ARTICLES = re.compile(r"^(the|a|an)\s+", re.IGNORECASE)
_NON_WORD = re.compile(r"[^a-z0-9\s]")
_WHITESPACE = re.compile(r"\s+")
_SENTENCE = re.compile(r"[.!?]+")


def normalize(text: str) -> str:
    """Lowercase, strip a leading article and punctuation, and collapse spaces."""

    lowered = text.strip().lower()
    lowered = _ARTICLES.sub("", lowered)
    lowered = _NON_WORD.sub("", lowered)
    return _WHITESPACE.sub(" ", lowered).strip()


def split_sentences(text: str) -> list[str]:
    """Split text into non-empty, stripped sentences."""

    return [part.strip() for part in _SENTENCE.split(text) if part.strip()]
