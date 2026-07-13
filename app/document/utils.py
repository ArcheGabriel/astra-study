import html
import re
import unicodedata


HTML_TAG_PATTERN = re.compile(
    r"<[^>]+>"
)

MARKDOWN_PATTERN = re.compile(
    r"[*_`~]"
)

WHITESPACE_PATTERN = re.compile(
    r"\s+"
)

CAPTION_PATTERN = re.compile(
    r"^(Figure|Fig\.?|Table)\s+\d+",
    re.IGNORECASE,
)

PAGE_NUMBER_PATTERN = re.compile(
    r"^\d+$"
)


def clean_text(
    text: str,
) -> str:
    """
    Normalize extracted Markdown text into clean text.
    """

    if not text:
        return ""

    # Decode HTML entities
    text = html.unescape(text)

    # Replace HTML tags with spaces
    text = HTML_TAG_PATTERN.sub(
        " ",
        text,
    )

    # Remove Markdown formatting
    text = MARKDOWN_PATTERN.sub(
        "",
        text,
    )

    # Unicode normalization
    text = unicodedata.normalize(
        "NFKC",
        text,
    )

    # Remove soft hyphen
    text = text.replace(
        "\u00ad",
        "",
    )

    # Remove zero-width spaces
    text = text.replace(
        "\u200b",
        "",
    )

    # Fix line-break hyphenation
    text = re.sub(
        r"(\w)-\s+(\w)",
        r"\1\2",
        text,
    )

    # Collapse whitespace
    text = WHITESPACE_PATTERN.sub(
        " ",
        text,
    )

    return text.strip()


def is_caption(
    text: str,
) -> bool:
    """
    Returns True if the text looks like a figure/table caption.
    """

    return bool(
        CAPTION_PATTERN.match(
            clean_text(text),
        )
    )


def is_page_number(
    text: str,
) -> bool:
    """
    Returns True for standalone page numbers.
    """

    return bool(
        PAGE_NUMBER_PATTERN.match(
            clean_text(text),
        )
    )


def is_image_text(
    text: str,
) -> bool:
    """
    Detect OCR text produced for images.

    This will evolve as we add Docling and
    multimodal parsing.
    """

    cleaned = clean_text(
        text,
    ).lower()

    return (
        "start of picture text" in cleaned
        or "end of picture text" in cleaned
        or "ocr" in cleaned
    )