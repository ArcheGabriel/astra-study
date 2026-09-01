from enum import StrEnum


class BlockType(StrEnum):
    """
    Represents the semantic type of a document block.

    This enum is parser-independent and is shared across
    ingestion, chunking, embeddings and retrieval.

    Every parser (Docling, OCR, etc.)
    should map its native output into one of these types.
    """

    # ---------- Text ----------

    HEADING = "heading"

    TEXT = "text"

    LIST = "list"

    QUOTE = "quote"

    CODE = "code"

    FORMULA = "formula"

    # ---------- Structured content ----------

    TABLE = "table"

    CAPTION = "caption"

    IMAGE = "image"

    IMAGE_TEXT = "image_text"

    # ---------- Page structure ----------

    HEADER = "header"

    FOOTER = "footer"

    PAGE_NUMBER = "page_number"

    # ---------- Fallback ----------

    UNKNOWN = "unknown"
