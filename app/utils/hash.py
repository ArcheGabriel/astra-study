from hashlib import sha256
from pathlib import Path


def calculate_sha256(
    file_path: Path,
) -> str:
    """
    Calculate the SHA-256 checksum of a file.
    """

    hash_object = sha256()

    with file_path.open(
        "rb",
    ) as file:

        while chunk := file.read(
            8192,
        ):
            hash_object.update(
                chunk,
            )

    return hash_object.hexdigest()