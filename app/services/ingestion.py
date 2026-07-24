import time

from app.chunking.pipeline import ChunkPipeline
from app.enums.document import DocumentStatus
from app.ingestion.factory import ProcessorFactory
from app.repositories.document import DocumentRepository
from app.search.hybrid.pipeline import HybridPipeline
from app.storage.base import BaseStorageService


class IngestionService:
    """
    Coordinates the complete ingestion workflow.

    Responsibilities
    ----------------
    1. Load uploaded document
    2. Extract semantic blocks
    3. Run chunk pipeline
    4. Generate embeddings
    5. Index vectors into Qdrant
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_service: BaseStorageService,
        hybrid_pipeline: HybridPipeline | None = None,
    ) -> None:

        self.document_repository = document_repository

        self.storage_service = storage_service

        self.chunking_pipeline = ChunkPipeline()

        self.hybrid_pipeline = (
            hybrid_pipeline
            or HybridPipeline()
        )

    def ingest_document(
        self,
        *,
        document_id: int,
    ) -> None:

        document = self.document_repository.get_by_id(
            document_id,
        )

        if document is None:
            return

        self.document_repository.update_status(
            document_id=document.id,
            status=DocumentStatus.PROCESSING,
        )

        try:

            file_path = self.storage_service.get_file_path(
                document.stored_filename,
            )

            processor = ProcessorFactory.get_processor(
                file_path,
            )

            extraction_result = processor.extract(
                file_path,
            )

            #
            # Replace the storage filename with the original
            # filename uploaded by the user.
            #
            extraction_result.metadata.file_name = (
                document.filename
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

            chunks = self.chunking_pipeline.run(
                extraction_result,
            )
            
            for chunk in chunks:
                chunk.metadata.user_id = document.user_id
            
            if not chunks:
                raise ValueError(
                    "No chunks were generated from the uploaded document."
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
                    f"Type : {chunk.metadata.block_type.value}"
                )

                print()

                print(
                    chunk.text[:250],
                )

                print()

            #
            # Generate embeddings and index into Qdrant
            #
            print("=" * 80)
            print("INDEXING INTO QDRANT")
            print("=" * 80)

            self.hybrid_pipeline.index(
                chunks,
            )


            #
            # Simulate downstream work if required.
            #
            self.document_repository.update_status(
                document_id=document.id,
                status=DocumentStatus.INDEXED,
            )
            
            print("Document indexed successfully.")

        except Exception as exc:

            self.document_repository.update_status(
                document_id=document.id,
                status=DocumentStatus.FAILED,
            )

            print(f"Ingestion failed: {exc}")

            raise