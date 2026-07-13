from __future__ import annotations

import hashlib
from uuid import UUID
from uuid import NAMESPACE_URL
from uuid import uuid5

from app.chunking.models import (
    ChunkMetadata,
    DocumentChunk,
)
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.tokens import (
    count_tokens,
)


class FinalizeStage(BaseChunkStage):
    """
    Final stage executed before embeddings.

    Responsibilities
    ----------------
    • Populate token count
    • Populate character count
    • Generate deterministic document UUID
    • Generate deterministic parent UUID
    • Generate deterministic chunk UUID
    • Normalize metadata
    • Validate final output

    This stage NEVER modifies chunk text.
    """

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        parent_uuid_cache: dict[
            int,
            UUID,
        ] = {}

        for chunk in chunks:

            metadata = chunk.metadata

            #
            # -----------------------------------------
            # Character count
            # -----------------------------------------
            #

            metadata.character_count = len(
                chunk.text,
            )

            #
            # -----------------------------------------
            # Token count
            # -----------------------------------------
            #
            

            metadata.token_count = count_tokens(
                chunk.text,
            )

            #
            # -----------------------------------------
            # Document UUID
            # -----------------------------------------
            #

            if metadata.document_uuid is None:

                metadata.document_uuid = (
                    self._document_uuid(
                        metadata,
                    )
                )

            #
            # -----------------------------------------
            # Parent UUID
            # -----------------------------------------
            #

            if chunk.parent_chunk is not None:

                if (
                    chunk.parent_chunk
                    not in parent_uuid_cache
                ):

                    parent_uuid_cache[
                        chunk.parent_chunk
                    ] = self._parent_uuid(
                        metadata.document_uuid,
                        chunk.parent_chunk,
                    )

                metadata.parent_chunk_uuid = (
                    parent_uuid_cache[
                        chunk.parent_chunk
                    ]
                )

            #
            # -----------------------------------------
            # Chunk UUID
            # -----------------------------------------
            #

            # Every chunk receives its own deterministic UUID.
            # Never preserve a copied UUID from a parent.

            metadata.chunk_uuid = self._chunk_uuid(
                chunk,
            )

            #
            # -----------------------------------------
            # Normalize metadata
            # -----------------------------------------
            #

            self._normalize(
                metadata,
            )

            #
            # -----------------------------------------
            # Validate
            # -----------------------------------------
            #

            self._validate(
                chunk,
            )

        return chunks

    def _document_uuid(
        self,
        metadata: ChunkMetadata,
    ) -> UUID:

        value = (
            metadata.checksum
            or metadata.document_name
            or "unknown-document"
        )

        return uuid5(
            NAMESPACE_URL,
            value,
        )

    def _parent_uuid(
        self,
        document_uuid: UUID,
        parent_chunk: int,
    ) -> UUID:

        return uuid5(
            document_uuid,
            f"parent-{parent_chunk}",
        )
    
    def _chunk_uuid(
        self,
        chunk: DocumentChunk,
    ) -> UUID:
        """
            Generate a deterministic UUID for every chunk.

            UUIDs must satisfy:

            • Stable across runs
            • Different recursive children get different UUIDs
            • Independent of Python's randomized hash()
        """

        metadata = chunk.metadata

        text_hash = hashlib.sha256(
            chunk.text.encode(
                "utf-8",
            )
        ).hexdigest()

        value = "|".join(
            [
                str(chunk.chunk_index),
                str(chunk.parent_chunk),
                str(metadata.page_start),
                str(metadata.page_end),
                str(metadata.block_start),
                str(metadata.block_end),
                str(metadata.section_id),
                str(metadata.heading_level),
                text_hash,
            ]
        )

        return uuid5(
            metadata.document_uuid,
            value,
        )

    def _normalize(
        self,
        metadata: ChunkMetadata,
    ) -> None:
        """
        Normalize page/block ranges.

        Pages should always be ascending.

        Block ranges are normalized only when the
        chunk resides completely on a single page.
        """

        #
        # Page range
        #

        if (

            metadata.page_start is not None

            and metadata.page_end is not None

            and metadata.page_start > metadata.page_end

        ):

            (
                metadata.page_start,
                metadata.page_end,
            ) = (
                metadata.page_end,
                metadata.page_start,
            )

        #
        # Block range
        #
        # IMPORTANT:
        #
        # Block numbering restarts from zero on every
        # page, therefore
        #
        # Page 24 : block 14
        # Page 25 : block 1
        #
        # is perfectly valid.
        #
        # Only normalize ranges that are completely
        # inside one page.
        #

        if (

            metadata.page_start
            == metadata.page_end

            and metadata.block_start is not None

            and metadata.block_end is not None

            and metadata.block_start > metadata.block_end

        ):

            (
                metadata.block_start,
                metadata.block_end,
            ) = (
                metadata.block_end,
                metadata.block_start,
            )

    def _validate(
        self,
        chunk: DocumentChunk,
    ) -> None:

        metadata = chunk.metadata

        #
        # Empty text
        #

        if not chunk.text.strip():

            raise ValueError(
                f"Chunk {chunk.chunk_index} is empty."
            )

        #
        # Missing document UUID
        #

        if metadata.document_uuid is None:

            raise ValueError(
                f"Chunk {chunk.chunk_index} "
                f"has no document UUID."
            )

        #
        # Missing chunk UUID
        #

        if metadata.chunk_uuid is None:

            raise ValueError(
                f"Chunk {chunk.chunk_index} "
                f"has no chunk UUID."
            )

        #
        # Invalid page start
        #

        if (

            metadata.page_start is not None

            and metadata.page_start <= 0

        ):

            raise ValueError(
                f"Invalid page_start "
                f"{metadata.page_start}"
            )

        #
        # Invalid page end
        #

        if (

            metadata.page_end is not None

            and metadata.page_end <= 0

        ):

            raise ValueError(
                f"Invalid page_end "
                f"{metadata.page_end}"
            )
        
        #
        # Page range validation
        #

        if (

            metadata.page_start is not None

            and metadata.page_end is not None

            and metadata.page_start > metadata.page_end

        ):

            raise ValueError(
                "Invalid page range "
                f"{metadata.page_start}"
                " -> "
                f"{metadata.page_end}"
            )

        #
        # Block range validation
        #
        # IMPORTANT
        #
        # Block numbering restarts on every page.
        #
        # Therefore
        #
        # Page 3  Block 14
        # Page 4  Block 1
        #
        # is perfectly valid.
        #
        # We only validate ordering when both
        # blocks belong to the SAME page.
        #

        if (

            metadata.page_start is not None

            and metadata.page_end is not None

            and metadata.page_start == metadata.page_end

            and metadata.block_start is not None

            and metadata.block_end is not None

            and metadata.block_start > metadata.block_end

        ):

            raise ValueError(
                "Invalid block range "
                f"{metadata.block_start}"
                " -> "
                f"{metadata.block_end}"
            )

        #
        # Character count validation
        #

        expected_characters = len(
            chunk.text,
        )

        if (
            metadata.character_count
            != expected_characters
        ):

            raise ValueError(
                f"Character count mismatch "
                f"for chunk "
                f"{chunk.chunk_index}"
            )

        #
        # Token count validation
        #

        expected_tokens = count_tokens(
            chunk.text,
        )

        if (
            metadata.token_count
            != expected_tokens
        ):

            raise ValueError(
                f"Token count mismatch "
                f"for chunk "
                f"{chunk.chunk_index}"
            )

        #
        # Section consistency
        #

        if (

            metadata.heading_path

            and metadata.section_title

            and metadata.heading_path[-1]
            != metadata.section_title

        ):

            raise ValueError(
                f"Heading path mismatch "
                f"for chunk "
                f"{chunk.chunk_index}"
            )

        #
        # Parent UUID consistency
        #

        if (

            chunk.parent_chunk is None

            and metadata.parent_chunk_uuid
            is not None

        ):

            raise ValueError(
                f"Chunk "
                f"{chunk.chunk_index} "
                "has a parent UUID but "
                "is not marked as a child."
            )

        if (

            chunk.parent_chunk is not None

            and metadata.parent_chunk_uuid
            is None

        ):

            raise ValueError(
                f"Chunk "
                f"{chunk.chunk_index} "
                "is missing its parent UUID."
            )