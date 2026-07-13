from openai.types.responses import response_mcp_call_failed_event
from openai.types.responses import response_mcp_call_failed_event
from copy import deepcopy

from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.splitter import split_for_embeddings
from app.chunking.utils.tokens import (
    count_tokens,
    join_sentences,
)


class RecursiveStage(BaseChunkStage):
    """
    Splits oversized semantic chunks into embedding-sized chunks.

    Characteristics
    ---------------
    ✓ Paragraph aware
    ✓ Sentence aware
    ✓ Token aware
    ✓ Sliding overlap
    ✓ Preserves metadata
    ✓ Preserves section hierarchy
    ✓ Stable parent-child relationship
    """

    MAX_TOKENS = 700

    OVERLAP_TOKENS = 100

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        output: list[DocumentChunk] = []

        next_chunk_index = 0

        next_parent_index = 0

        for chunk in chunks:

            tokens = count_tokens(
                chunk.text,
            )

            #
            # Chunk already suitable for embeddings.
            #
            if tokens <= self.MAX_TOKENS:

                chunk.chunk_index = next_chunk_index

                next_chunk_index += 1

                output.append(
                    chunk,
                )

                continue

            #
            # Oversized semantic section.
            #
            parent_chunk = next_parent_index

            next_parent_index += 1

            children = self._split_chunk(

                chunk=chunk,

                parent_chunk=parent_chunk,

                start_chunk_index=next_chunk_index,

            )

            next_chunk_index += len(
                children,
            )

            output.extend(
                children,
            )

        return output

    def _split_chunk(
        self,
        chunk: DocumentChunk,
        parent_chunk: int,
        start_chunk_index: int,
    ) -> list[DocumentChunk]:
        """
        Split one semantic chunk into multiple
        embedding chunks.
        """

        heading = ""

        body = chunk.text

        #
        # Preserve heading only once.
        #
        if chunk.metadata.section_title:

            heading = chunk.metadata.section_title.strip()

            if body.startswith(
                heading,
            ):

                body = body[
                    len(heading):
                :].strip()
        
        #
        # Reserve room for the heading.
        #
        heading_tokens = 0

        if heading:

            heading_tokens = count_tokens(
                heading,
            )

        effective_max_tokens = (
            self.MAX_TOKENS - heading_tokens
        )


        windows = split_for_embeddings(

            text=body,

            max_tokens=effective_max_tokens,

            overlap_tokens=self.OVERLAP_TOKENS,

        )
        
        
        #
        # Fallback for pathological documents.
        #
        if not windows:

            windows = [[body]]

        children: list[
            DocumentChunk
        ] = []

        for i, window in enumerate(
            windows,
        ):

            metadata = deepcopy(
                chunk.metadata,
            )
            
            #
            # Recursive children must receive fresh UUIDs
            # during FinalizeStage.
            #
            metadata.chunk_uuid = None
            metadata.parent_chunk_uuid = None

            text = join_sentences(
                window,
            )

            

            #
            # Preserve heading on first child only.
            #
            if i == 0 and heading:

                text = (
                    heading
                    + "\n\n"
                    + text
                )

            child = DocumentChunk(

                text=text,

                chunk_index=start_chunk_index + i,

                metadata=metadata,

                parent_chunk=parent_chunk,

            )


            children.append(
                child,
            )

        return children
