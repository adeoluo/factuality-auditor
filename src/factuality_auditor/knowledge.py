"""A trusted knowledge base of facts used to verify claims.

Relations here are **functional**: a subject and relation fix a single correct
object (a country has one capital, an element one symbol). This is what lets the
auditor *refute* a claim, not merely fail to support it: if a claim asserts a
different object for a known subject and relation, it contradicts the base.
"""

from __future__ import annotations

from collections.abc import Iterable

from factuality_auditor.text import normalize
from factuality_auditor.types import Fact

# The set of relations the auditor understands, all functional.
RELATIONS: frozenset[str] = frozenset(
    {"capital_of", "located_in", "born_in", "symbol_is", "moon_count"}
)


class KnowledgeBase:
    """An index of functional facts supporting lookup and contradiction checks."""

    def __init__(self, facts: Iterable[Fact]) -> None:
        self._by_key: dict[tuple[str, str], Fact] = {}
        for fact in facts:
            self._by_key[fact.key()] = fact

    def __len__(self) -> int:
        return len(self._by_key)

    def canonical(self, subject: str, relation: str) -> Fact | None:
        """Return the known fact for a subject and relation, if any."""

        return self._by_key.get((normalize(subject), relation))

    @classmethod
    def from_triples(cls, triples: Iterable[tuple[str, str, str]]) -> KnowledgeBase:
        """Build a knowledge base from raw (subject, relation, object) triples."""

        facts = [
            Fact(normalize(subject), relation, normalize(object_))
            for subject, relation, object_ in triples
        ]
        return cls(facts)
