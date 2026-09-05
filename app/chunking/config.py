from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChunkingConfig:
    """Single source of truth for the chunking pipeline's size limits.

    Every value is a token count for ``text-embedding-3-large`` (tiktoken).
    These are the limits the individual stages historically hard-coded; they
    are collected here so the chunking contract lives in one place. They are
    intentionally **not** tuned in this phase -- only centralised.
    """

    # Hard ceiling for any chunk that will be embedded. RecursiveStage splits
    # anything larger; nothing downstream is allowed to merge past it.
    embed_max: int = 700

    # Sentence-window overlap, applied ONLY when an oversized section is split.
    overlap: int = 100

    # A chunk below this many tokens is a candidate for merging into an
    # adjacent chunk of the SAME section.
    merge_min: int = 120

    # Size of the pre-split "semantic section" MergeStage accumulates before
    # RecursiveStage windows it down to ``embed_max``.
    section_soft: int = 1200
    section_hard: int = 1600


# Process-wide default. Stages accept an override for testing.
DEFAULT_CHUNKING_CONFIG = ChunkingConfig()
