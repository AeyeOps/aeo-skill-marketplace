"""
Nous Lens Framework

Provides the lens-based extraction infrastructure for the Nous observation system.
"""

from .base import ExtractionLens, parse_jsonl, build_extraction_prompt, flush_inbox
from .learnings import LEARNINGS_LENS
from .knowledge import KNOWLEDGE_LENS
from .models import StatuslineEntry, LearningSignal, KnowledgeSignal

__all__ = [
    "ExtractionLens",
    "parse_jsonl",
    "build_extraction_prompt",
    "flush_inbox",
    "LEARNINGS_LENS",
    "KNOWLEDGE_LENS",
    "StatuslineEntry",
    "LearningSignal",
    "KnowledgeSignal",
]
