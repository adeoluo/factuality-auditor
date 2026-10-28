"""A bundled knowledge base and a labeled set of answers to audit.

An answer is labeled ``hallucinated`` when it contains a false claim, and
``factual`` otherwise. Crucially, some false claims are **refutable** (the
knowledge base holds a contradicting fact) while others are **unverifiable**
(the subject is outside the knowledge base). The auditor catches the refutable
ones with high confidence and abstains, with low confidence, on the rest, which
is exactly what the detection and calibration numbers reveal.
"""

from __future__ import annotations

from dataclasses import dataclass

from factuality_auditor.knowledge import KnowledgeBase

KNOWLEDGE = KnowledgeBase.from_triples(
    [
        ("Paris", "capital_of", "France"),
        ("Tokyo", "capital_of", "Japan"),
        ("Canberra", "capital_of", "Australia"),
        ("The Eiffel Tower", "located_in", "Paris"),
        ("Gold", "symbol_is", "Au"),
        ("Oxygen", "symbol_is", "O"),
        ("Mars", "moon_count", "2"),
        ("Earth", "moon_count", "1"),
    ]
)


@dataclass(frozen=True)
class LabeledAnswer:
    """A generated answer with its gold factuality label."""

    text: str
    hallucinated: bool


ANSWERS: tuple[LabeledAnswer, ...] = (
    # Supported: factual and verifiable (auditor is confident and correct).
    LabeledAnswer("Paris is the capital of France.", False),
    LabeledAnswer("Tokyo is the capital of Japan.", False),
    LabeledAnswer("The symbol for Gold is Au.", False),
    LabeledAnswer("The Eiffel Tower is located in Paris.", False),
    # Refuted: hallucinated and refutable (auditor flags with high confidence).
    LabeledAnswer("Paris is the capital of Germany.", True),
    LabeledAnswer("Tokyo is the capital of China.", True),
    LabeledAnswer("The symbol for Gold is Pb.", True),
    LabeledAnswer("The Eiffel Tower is located in Rome.", True),
    LabeledAnswer("Mars has 5 moons.", True),
    # Unverifiable and factual (auditor abstains with low confidence, correct).
    LabeledAnswer("Oslo is the capital of Norway.", False),
    LabeledAnswer("Berlin is in Germany.", False),
    LabeledAnswer("Lisbon is the capital of Portugal.", False),
    LabeledAnswer("Madrid is the capital of Spain.", False),
    # Unverifiable but hallucinated (auditor abstains, low confidence, misses).
    LabeledAnswer("Sydney is the capital of Australia.", True),
    LabeledAnswer("Venus has 3 moons.", True),
)
