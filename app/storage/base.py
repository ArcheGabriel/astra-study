from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile


class BaseStorageService(ABC):
    """
    Base interface for all storage providers.
    """

    @abstractmethod
    async def save_file(
        self,
        file: UploadFile,
    ) -> tuple[str, int]:
        """
        Save a file and return:

        (
            stored_filename,
            file_size,
        )
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_file(
        self,
        stored_filename: str,
    ) -> None:
        """
        Delete a stored file.
        """
        raise NotImplementedError

    @abstractmethod
    def get_file_path(
        self,
        stored_filename: str,
    ) -> Path:
        """
        Return the absolute path of a stored file.
        """
        raise NotImplementedError