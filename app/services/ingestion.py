import time

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

        print("=" * 60)
        print("Extraction Completed")
        print("=" * 60)

        print(extraction_result.metadata)

        print(f"Pages extracted: {len(extraction_result.pages)}")

        total_paragraphs = 0

        page = extraction_result.pages[1]

        print()
        print("=" * 80)
        print("PAGE 2")
        print("=" * 80)

        for paragraph in page.paragraphs:

            print("-" * 60)

            print(
                f"Block {paragraph.block_index}"
            )

            print(
                f"Type : {paragraph.block_type}"
            )

            print()

            print(paragraph.text)

            print()

        time.sleep(10)

        self.document_repository.update_status(
            document_id=document.id,
            status=DocumentStatus.INDEXED,
        )