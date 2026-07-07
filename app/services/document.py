from pathlib import Path

from fastapi import UploadFile

from app.enums.document import DocumentStatus
from app.exceptions.document import DocumentNotFoundError
from app.models.document import Document
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentResponse
from app.storage.base import BaseStorageService
from app.validators.document import DocumentValidator


class DocumentService:
    """
    Handles document upload business logic.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_service: BaseStorageService,
    ) -> None:
        self.document_repository = document_repository
        self.storage_service = storage_service

    async def upload_documents(
        self,
        *,
        files: list[UploadFile],
        current_user: User,
    ) -> list[Document]:
        """
        Upload one or more documents.

        Returns the created Document models.
        """

        uploaded_documents: list[Document] = []

        for file in files:

            await DocumentValidator.validate(
                file,
            )

            stored_filename, file_size = (
                await self.storage_service.save_file(
                    file,
                )
            )

            document = Document(
                user_id=current_user.id,
                filename=file.filename,
                stored_filename=stored_filename,
                content_type=file.content_type,
                file_size=file_size,
                status=DocumentStatus.UPLOADED,
            )

            created_document = (
                self.document_repository.create(
                    document,
                )
            )

            uploaded_documents.append(
                created_document,
            )

        return uploaded_documents

    def get_documents(
        self,
        *,
        current_user: User,
    ) -> list[DocumentResponse]:
        """
        Retrieve all documents belonging to the current user.
        """

        documents = (
            self.document_repository.get_by_user(
                current_user.id,
            )
        )

        return [
            DocumentResponse.model_validate(
                document,
            )
            for document in documents
        ]

    def get_document(
        self,
        *,
        document_id: int,
        current_user: User,
    ) -> DocumentResponse:
        """
        Retrieve a single document belonging to the current user.
        """

        document = (
            self.document_repository.get_by_id_and_user(
                document_id=document_id,
                user_id=current_user.id,
            )
        )

        if document is None:
            raise DocumentNotFoundError()

        return DocumentResponse.model_validate(
            document,
        )

    async def delete_document(
        self,
        *,
        document_id: int,
        current_user: User,
    ) -> None:
        """
        Delete a document and its associated file.
        """

        document = (
            self.document_repository.get_by_id_and_user(
                document_id=document_id,
                user_id=current_user.id,
            )
        )

        if document is None:
            raise DocumentNotFoundError()

        await self.storage_service.delete_file(
            document.stored_filename,
        )

        self.document_repository.delete(
            document,
        )

    def download_document(
        self,
        *,
        document_id: int,
        current_user: User,
    ) -> tuple[Path, str]:
        """
        Return the file path and original filename.
        """

        document = (
            self.document_repository.get_by_id_and_user(
                document_id=document_id,
                user_id=current_user.id,
            )
        )

        if document is None:
            raise DocumentNotFoundError()

        file_path = (
            self.storage_service.get_file_path(
                document.stored_filename,
            )
        )

        return (
            file_path,
            document.filename,
        )