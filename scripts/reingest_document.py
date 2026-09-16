"""Re-run one document through the production ingestion path.

    Document.id (SQLite)
        -> load the authoritative Document row
        -> LocalStorageService.get_file_path (stored file on disk)
        -> ProcessorFactory / DoclingProcessor.extract
        -> ChunkPipeline.run
        -> stamp RBAC fields from the loaded Document row
        -> HybridPipeline.index   (Qdrant)   [only with --commit]

This reuses the exact production components (`app.ingestion`, `app.chunking`,
`app.search.hybrid`, `app.storage`). It does NOT invent an indexing path.

RBAC-5F
-------
Every Qdrant point this script can write is a ``schema_version=3`` point
(the same ``HybridPipeline``/``HybridMapper`` path production ingestion
uses), and RBAC-5C/5D/5E's authorization filters and safe deletion both
depend on that payload's ``document_id``/``organisation_id``/``team_id``/
``access_scope``/``user_id`` fields being correct. Those five fields are
sourced *exclusively* from the one authoritative ``Document`` row loaded
by ``--document-id`` -- never independently supplied on the command line
-- so a reingested document can never end up with mismatched, guessed, or
another document's RBAC metadata. ``team_id`` is preserved exactly as
stored (``None`` for INDIVIDUAL/ORGANISATION documents is legitimate and
is never coerced or rejected).

Safety
------
* Default mode is a DRY RUN: load the Document row, extract, chunk, and
  print a summary, then STOP. Nothing is embedded and nothing is written
  to Qdrant.
* Writing to Qdrant requires BOTH ``--commit`` and
  ``--yes-write-to-qdrant``. Without both, the script refuses.
* The script reads the ``documents`` table (to resolve the authoritative
  RBAC fields and stored file path for ``--document-id``) but never
  writes to it -- no row is created, updated, or deleted, and no status
  transition occurs. It only upserts vectors for the chunks it produced.
* If ``--document-id`` does not resolve to an existing row, the script
  refuses to proceed -- no extraction, no chunking, no Qdrant write.

Stage 5 note: the Stage 5 evaluation MUST NOT call this script. Use
``evaluation/chunking_report.py`` for offline analysis.

Usage
-----
    uv run python -m scripts.reingest_document --document-id 42
    uv run python -m scripts.reingest_document --document-id 42 \
        --commit --yes-write-to-qdrant
"""

from __future__ import annotations

import argparse
import sys

from app.chunking.pipeline import ChunkPipeline
from app.database.session import SessionLocal
from app.ingestion.factory import ProcessorFactory
from app.models.document import Document
from app.repositories.document import DocumentRepository
from app.storage.local import LocalStorageService


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


def _stamp_rbac_fields(chunks, document: Document) -> None:
    """
    Stamp every chunk's metadata from the one authoritative Document row.

    Replicates IngestionService.ingest_document's existing five-field
    stamping loop verbatim (app/services/ingestion.py) -- the reference
    implementation is not modified; this script performs the identical
    assignment for its own, separate chunk list. team_id/access_scope are
    copied exactly as stored (team_id legitimately None for INDIVIDUAL/
    ORGANISATION documents) -- never defaulted, coerced, or guessed.
    """

    for chunk in chunks:
        chunk.metadata.user_id = document.user_id
        chunk.metadata.document_id = document.id
        chunk.metadata.organisation_id = document.organisation_id
        chunk.metadata.team_id = document.team_id
        chunk.metadata.access_scope = document.access_scope


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reingest_document")
    parser.add_argument(
        "--document-id", required=True, type=int,
        help="id of the existing Document row to re-ingest -- RBAC "
             "fields and the stored file path are both read from it",
    )
    parser.add_argument("--commit", action="store_true",
                        help="also embed and upsert vectors into Qdrant")
    parser.add_argument("--yes-write-to-qdrant", action="store_true",
                        help="required acknowledgement alongside --commit")
    args = parser.parse_args(argv)

    db = SessionLocal()
    try:
        document = DocumentRepository(db).get_by_id(args.document_id)

        if document is None:
            print(
                f"error: no document found with id={args.document_id}",
                file=sys.stderr,
            )
            return 2

        # Every field this script needs is a plain scalar column already
        # loaded by the query above (no relationship access) -- the ORM
        # instance stays safely readable after db.close() below; only a
        # lazy-loaded/relationship attribute would require the session
        # to still be open.
        stored_filename = document.stored_filename
    finally:
        db.close()

    file_path = LocalStorageService().get_file_path(stored_filename)

    if not file_path.exists():
        print(f"error: stored file not found: {file_path}", file=sys.stderr)
        return 2

    print(f"[1/3] extracting     : document_id={document.id} ({file_path})")
    processor = ProcessorFactory.get_processor(file_path)
    extraction = processor.extract(file_path)
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

    _stamp_rbac_fields(chunks, document)

    access_scope_value = document.access_scope.value if document.access_scope else None
    print(
        f"[3/3] indexing into Qdrant "
        f"(document_id={document.id}, user_id={document.user_id}, "
        f"organisation_id={document.organisation_id}, team_id={document.team_id}, "
        f"access_scope={access_scope_value}) ..."
    )
    from app.search.hybrid.pipeline import HybridPipeline

    HybridPipeline().index(chunks)
    print("      done. vectors upserted (relational DB untouched).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
