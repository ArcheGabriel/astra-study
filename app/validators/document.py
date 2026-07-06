from fastapi import UploadFile

from app.config.settings import settings
from app.constants.document import SUPPORTED_DOCUMENT_TYPES
from app.exceptions.document import (
    DocumentTooLargeError,
    EmptyDocumentError,
    InvalidDocumentTypeError,
)


class DocumentValidator:
    """
    Validates uploaded study documents.
    """

    @classmethod
    async def validate(
        cls,
        file: UploadFile,
    ) -> None:
        """
        Validate an uploaded document.
        """

        if file.content_type not in SUPPORTED_DOCUMENT_TYPES:
            raise InvalidDocumentTypeError()

        content = await file.read()

        if len(content) == 0:
            raise EmptyDocumentError()

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        if len(content) > max_size:
            raise DocumentTooLargeError()

        await file.seek(0)