"""Extract atomic factual claims from text as (subject, relation, object) triples.

Extraction is rule-based: a set of surface patterns map sentences to functional
relations the knowledge base understands. Rules are deterministic and
inspectable; a model-backed extractor drops in behind ``extract_claims``.
"""

from __future__ import annotations

import re

from factuality_auditor.text import normalize, split_sentences
from factuality_auditor.types import Claim, Fact

# A middle phrase is matched non-greedily; a trailing phrase greedily.
_MID = r"([A-Za-z][A-Za-z0-9 ]*?)"
_END = r"([A-Za-z][A-Za-z0-9 ]*)"
_NUM = r"(\d+)"

_PATTERNS: tuple[tuple[re.Pattern[str], str, bool], ...] = (
    # pattern, relation, subject_is_first_group
    (re.compile(rf"the capital of {_MID} is {_END}", re.IGNORECASE), "capital_of", False),
    (re.compile(rf"{_MID} is the capital of {_END}", re.IGNORECASE), "capital_of", True),
    (re.compile(rf"{_MID} is located in {_END}", re.IGNORECASE), "located_in", True),
    (re.compile(rf"{_MID} was born in {_END}", re.IGNORECASE), "born_in", True),
    (re.compile(rf"the chemical symbol of {_MID} is {_END}", re.IGNORECASE), "symbol_is", True),
    (re.compile(rf"the symbol for {_MID} is {_END}", re.IGNORECASE), "symbol_is", True),
    (re.compile(rf"{_MID} has {_NUM} moons", re.IGNORECASE), "moon_count", True),
    (re.compile(rf"{_MID} is in {_END}", re.IGNORECASE), "located_in", True),
)


def _claim_from_match(
    match: re.Match[str], relation: str, subject_first: bool, sentence: str
) -> Claim:
    first, second = match.group(1), match.group(2)
    subject, object_ = (first, second) if subject_first else (second, first)
    fact = Fact(normalize(subject), relation, normalize(object_))
    return Claim(fact=fact, source_text=sentence.strip())


def extract_claims(text: str) -> list[Claim]:
    """Extract all claims from text, one per matched relation per sentence."""

    claims: list[Claim] = []
    seen: set[tuple[str, str, str]] = set()
    for sentence in split_sentences(text):
        matched_relations: set[str] = set()
        for pattern, relation, subject_first in _PATTERNS:
            if relation in matched_relations:
                continue
            match = pattern.search(sentence)
            if not match:
                continue
            claim = _claim_from_match(match, relation, subject_first, sentence)
            matched_relations.add(relation)
            identity = (claim.fact.subject, claim.fact.relation, claim.fact.object)
            if identity not in seen:
                seen.add(identity)
                claims.append(claim)
    return claims
