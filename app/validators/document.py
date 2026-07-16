from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config.settings import settings


class DocumentValidator:
    """
    Validates uploaded documents before they are
    stored on disk.
    """

    @staticmethod
    async def validate(
        file: UploadFile,
    ) -> None:
        """
        Validate an uploaded document.

        Raises
        ------
        HTTPException
            If validation fails.
        """

        #
        # Filename
        #
        if not file.filename:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Uploaded file has no filename.",

            )

        #
        # Extension
        #
        extension = Path(
            file.filename,
        ).suffix.lower()

        if (
            extension
            not in settings.ALLOWED_DOCUMENT_EXTENSIONS
        ):

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail=(
                    f"Unsupported file type "
                    f"'{extension}'."
                ),

            )

        #
        # Content type
        #
        if (

            file.content_type

            not in settings.ALLOWED_CONTENT_TYPES

        ):

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail=(
                    f"Unsupported content type "
                    f"'{file.content_type}'."
                ),

            )

        #
        # File size
        #
        contents = await file.read()

        size = len(contents)

        await file.seek(0)

        max_size = (
            settings.MAX_UPLOAD_SIZE_MB
            * 1024
            * 1024
        )

        if size > max_size:

            raise HTTPException(

                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,

                detail=(
                    f"Maximum upload size is "
                    f"{settings.MAX_UPLOAD_SIZE_MB} MB."
                ),

            )

        #
        # Empty file
        #
        if size == 0:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Uploaded file is empty.",

            )