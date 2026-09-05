"""Re-run one document through the production ingestion path.

    document path
        -> ProcessorFactory / DoclingProcessor.extract
        -> ChunkPipeline.run
        -> HybridPipeline.index   (Qdrant)   [only with --commit]

This reuses the exact production components (`app.ingestion`, `app.chunking`,
`app.search.hybrid`). It does NOT invent an indexing path.

Safety
------
* Default mode is a DRY RUN: extract + chunk + print a summary, and STOP.
  Nothing is embedded and nothing is written to Qdrant or the database.
* Writing to Qdrant requires BOTH ``--commit`` and
  ``--yes-write-to-qdrant``. Without both, the script refuses.
* The script never touches the relational database (no document row, no
  status transition). It only upserts vectors for the chunks it produced.

Stage 5 note: the Stage 5 evaluation MUST NOT call this script. Use
``evaluation/chunking_report.py`` for offline analysis.

Usage
-----
    uv run python -m scripts.reingest_document --doc tests/test_documents/Attention.pdf
    uv run python -m scripts.reingest_document --doc <path> --user-id 7 \
        --commit --yes-write-to-qdrant
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.chunking.pipeline import ChunkPipeline
from app.ingestion.factory import ProcessorFactory


def _summarise(chunks) -> None:
    from collections import Counter

    from app.chunking.utils.tokens import count_tokens

    types = Counter(c.metadata.block_type.value for c in chunks)
    tokens = [count_tokens(c.text) for c in chunks]
    over = [c.chunk_index for c in chunks if count_tokens(c.text) > 700]
    print(f"  chunks              : {len(chunks)}")
    print(f"  effective types     : {dict(sorted(types.items()))}")
    if tokens:
        print(f"  tokens min/mean/max : {min(tokens)} / "
              f"{sum(tokens) // len(tokens)} / {max(tokens)}")
    print(f"  chunks > 700 tokens : {len(over)} {over}")
    print(f"  provenance coverage : "
          f"{sum(1 for c in chunks if c.metadata.provenance)}/{len(chunks)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reingest_document")
    parser.add_argument("--doc", required=True, type=Path)
    parser.add_argument("--user-id", type=int, default=None,
                        help="tenant id stamped on every chunk (required for --commit)")
    parser.add_argument("--commit", action="store_true",
                        help="also embed and upsert vectors into Qdrant")
    parser.add_argument("--yes-write-to-qdrant", action="store_true",
                        help="required acknowledgement alongside --commit")
    args = parser.parse_args(argv)

    if not args.doc.exists():
        print(f"error: no such file: {args.doc}", file=sys.stderr)
        return 2

    print(f"[1/3] extracting     : {args.doc}")
    processor = ProcessorFactory.get_processor(args.doc)
    extraction = processor.extract(args.doc)
    print(f"      source blocks  : {len(extraction.blocks)}")

    print("[2/3] chunking")
    chunks = ChunkPipeline().run(extraction)
    if not chunks:
        print("error: no chunks produced", file=sys.stderr)
        return 1
    _summarise(chunks)

    if not args.commit:
        print("[3/3] DRY RUN -- nothing written. Pass --commit "
              "--yes-write-to-qdrant to index.")
        return 0

    if not args.yes_write_to_qdrant:
        print("refusing to write: --commit also requires --yes-write-to-qdrant",
              file=sys.stderr)
        return 2
    if args.user_id is None:
        print("refusing to write: --user-id is required with --commit",
              file=sys.stderr)
        return 2

    for chunk in chunks:
        chunk.metadata.user_id = args.user_id

    print(f"[3/3] indexing into Qdrant (user_id={args.user_id}) ...")
    from app.search.hybrid.pipeline import HybridPipeline

    HybridPipeline().index(chunks)
    print("      done. vectors upserted (relational DB untouched).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
