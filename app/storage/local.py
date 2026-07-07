from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.storage.base import BaseStorageService


class LocalStorageService(BaseStorageService):
    """
    Stores uploaded files on the local filesystem.
    """

    def __init__(self) -> None:
        self.upload_directory = (
            Path("storage")
            / "uploads"
        )

        self.upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    async def save_file(
        self,
        file: UploadFile,
    ) -> tuple[str, int]:
        """
        Save an uploaded file.
        """

        extension = Path(
            file.filename,
        ).suffix

        stored_filename = (
            f"{uuid4()}{extension}"
        )

        destination = (
            self.upload_directory
            / stored_filename
        )

        content = await file.read()

        destination.write_bytes(
            content,
        )

        return (
            stored_filename,
            len(content),
        )

    async def delete_file(
        self,
        stored_filename: str,
    ) -> None:
        """
        Delete a stored file.
        """

        path = (
            self.upload_directory
            / stored_filename
        )

        if path.exists():
            path.unlink()

    def get_file_path(
        self,
        stored_filename: str,
    ) -> Path:
        """
        Return the absolute path of a stored file.
        """

        return (
            self.upload_directory
            / stored_filename
        )