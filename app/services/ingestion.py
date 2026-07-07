import time

from app.chunking.pipeline import ChunkPipeline
from app.enums.document import DocumentStatus
from app.ingestion.factory import ProcessorFactory
from app.repositories.document import DocumentRepository
from app.storage.base import BaseStorageService


class IngestionService:
    """
    Handles the document ingestion workflow.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_service: BaseStorageService,
    ) -> None:
        self.document_repository = document_repository
        self.storage_service = storage_service

    def ingest_document(
        self,
        *,
        document_id: int,
    ) -> None:
        """
        Run the ingestion pipeline.
        """

        document = self.document_repository.get_by_id(
            document_id,
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

        chunk_pipeline = ChunkPipeline()

        chunks = chunk_pipeline.run(
            extraction_result,
        )

        print("=" * 60)
        print("Chunking Completed")
        print("=" * 60)

        print()

        print(
            f"Chunks generated : {len(chunks)}"
        )

        print()

        for chunk in chunks[:10]:

            print("-" * 60)

            print(
                f"Chunk #{chunk.chunk_index}"
            )

            print(
                f"Page : {chunk.metadata.page_number}"
            )

            print(
                f"Block : {chunk.metadata.block_index}"
            )

            print(
                f"Type : {chunk.metadata.block_type.value}"
            )

            print()

            preview = (
                chunk.text[:250]
                .replace("\n", " ")
            )

            print(preview)

            print()

        # Simulate the remaining indexing work
        time.sleep(10)

        self.document_repository.update_status(
            document_id=document.id,
            status=DocumentStatus.INDEXED,
        )