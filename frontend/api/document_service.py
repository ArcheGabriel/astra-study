from __future__ import annotations

from typing import BinaryIO

from frontend.api.api_client import ApiClient
from frontend.models.document import Document


class DocumentService:
    """
    Service responsible for all document-related operations.
    """

    def __init__(
        self,
        client: ApiClient,
    ) -> None:
        self.client = client

    def list_documents(
        self,
    ) -> list[Document]:
        """
        Retrieve all uploaded documents.
        """

        response = self.client.get(
            "/documents",
        )

        return [
            Document.from_dict(item)
            for item in response
        ]

    def get_document(
        self,
        document_id: int,
    ) -> Document:
        """
        Retrieve metadata for a single document.
        """

        response = self.client.get(
            f"/documents/{document_id}",
        )

        return Document.from_dict(
            response,
        )

    def upload_documents(
        self,
        uploaded_files: list[BinaryIO],
    ) -> list[Document]:
        """
        Upload one or more documents.
        """

        files = []

        try:

            for uploaded_file in uploaded_files:

                uploaded_file.seek(0)

                files.append(
                    (
                        "files",
                        (
                            uploaded_file.name,
                            uploaded_file,
                            uploaded_file.type,
                        ),
                    )
                )

            response = self.client.post(
                "/documents/upload",
                files=files,
            )

        finally:
            for uploaded_file in uploaded_files:
                try:
                    uploaded_file.seek(0)
                except Exception:
                    pass

        #
        # Backend may return either:
        #   - a single Document
        #   - a list[Document]
        #

        if isinstance(response, list):

            return [
                Document.from_dict(item)
                for item in response
            ]

        return [
            Document.from_dict(response)
        ]

    def download_document(
        self,
        document_id: int,
    ) -> bytes:
        """
        Download the original uploaded document.
        """

        return self.client.get_bytes(
            f"/documents/{document_id}/download",
        )

    def delete_document(
        self,
        document_id: int,
    ) -> None:
        """
        Delete a document.
        """

        self.client.delete(
            f"/documents/{document_id}",
        )