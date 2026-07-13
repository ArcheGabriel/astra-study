import time

from app.chunking.pipeline import ChunkingService
from app.enums.document import DocumentStatus
from app.ingestion.factory import ProcessorFactory
from app.repositories.document import DocumentRepository
from app.storage.base import BaseStorageService


class IngestionService:
    """
    Coordinates the complete ingestion workflow.

    Responsibilities
    ----------------
    1. Load uploaded document
    2. Extract semantic blocks
    3. Run chunk pipeline
    4. (Later) Generate embeddings
    5. (Later) Store vectors
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_service: BaseStorageService,
    ) -> None:

        self.document_repository = (
            document_repository
        )

        self.storage_service = (
            storage_service
        )

        self.chunking_service = (
            ChunkingService()
        )

    def ingest_document(
        self,
        *,
        document_id: int,
    ) -> None:

        document = (
            self.document_repository.get_by_id(
                document_id,
            )
        )

        if document is None:
            return

        self.document_repository.update_status(
            document_id=document.id,
            status=DocumentStatus.PROCESSING,
        )

        file_path = (
            self.storage_service.get_file_path(
                document.stored_filename,
            )
        )

        processor = (
            ProcessorFactory.get_processor(
                file_path,
            )
        )

        extraction_result = (
            processor.extract(
                file_path,
            )
        )

        print("=" * 80)
        print("DOCUMENT EXTRACTION COMPLETED")
        print("=" * 80)

        print()

        print(extraction_result.metadata)

        print()

        print(
            f"Semantic Blocks : {len(extraction_result.blocks)}"
        )

        print()

        print("=" * 80)
        print("FIRST 10 BLOCKS")
        print("=" * 80)

        for block in extraction_result.blocks[:10]:

            print()

            print("-" * 60)

            print(
                f"Type : {block.block_type}"
            )

            print(
                f"Level : {block.level}"
            )

            print()

            print(
                block.text[:250],
            )

        chunks = (
            self.chunking_service.chunk(
                extraction_result,
            )
        )

        print()

        print("=" * 80)
        print("CHUNKING COMPLETED")
        print("=" * 80)

        print()

        print(
            f"Chunks Generated : {len(chunks)}"
        )

        print()

        for chunk in chunks[:10]:

            print("-" * 60)

            print(
                f"Chunk #{chunk.chunk_index}"
            )

            print(
                f"Type : {chunk.block_type}"
            )

            print()

            print(
                chunk.text[:250],
            )

            print()

        # Placeholder for future stages:
        #
        # embeddings = ...
        # vector_store.upsert(...)
        # metadata_store.save(...)

        time.sleep(2)

        self.document_repository.update_status(
            document_id=document.id,
            status=DocumentStatus.INDEXED,
        )