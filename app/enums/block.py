from enum import StrEnum


class BlockType(StrEnum):
    """
    Logical type assigned to an extracted text block.
    """

    TEXT = "text"

    CAPTION = "caption"

    LIST = "list"

    HEADER = "header"

    FOOTER = "footer"

    UNKNOWN = "unknown"