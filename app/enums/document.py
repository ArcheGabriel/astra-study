from enum import Enum


class DocumentStatus(
    str,
    Enum,
):
    """
    Processing state of a document.
    """

    UPLOADED = "uploaded"

    PROCESSING = "processing"

    INDEXED = "indexed"

    FAILED = "failed"