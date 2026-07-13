import re


_NUMERIC_PATTERN = re.compile(
    r"\d+$",
)

_PUNCTUATION_PATTERN = re.compile(
    r"[^\w\s]+$",
)

_PAGE_PATTERN = re.compile(
    r"^(page\s*)?\d+$",
    re.IGNORECASE,
)

_DOI_PATTERN = re.compile(
    r"^doi\s*[:.]",
    re.IGNORECASE,
)

_ISBN_PATTERN = re.compile(
    r"^isbn",
    re.IGNORECASE,
)

_COPYRIGHT_PATTERN = re.compile(
    r"^(©|copyright)",
    re.IGNORECASE,
)


def is_empty(
    text: str,
) -> bool:
    """
    Returns True if the text is empty.
    """

    return not text.strip()


def is_numeric_only(
    text: str,
) -> bool:
    """
    Returns True if the text contains only digits.
    """

    return bool(
        _NUMERIC_PATTERN.fullmatch(
            text.strip(),
        )
    )


def is_punctuation_only(
    text: str,
) -> bool:
    """
    Returns True if the text contains only punctuation.
    """

    stripped = text.strip()

    if not stripped:
        return False

    return bool(
        _PUNCTUATION_PATTERN.fullmatch(
            stripped,
        )
    )


def is_page_number(
    text: str,
) -> bool:
    """
    Detect page numbers.
    """

    return bool(
        _PAGE_PATTERN.fullmatch(
            text.strip(),
        )
    )


def is_copyright(
    text: str,
) -> bool:
    """
    Detect copyright lines.
    """

    return bool(
        _COPYRIGHT_PATTERN.match(
            text.strip(),
        )
    )


def is_doi(
    text: str,
) -> bool:
    """
    Detect DOI lines.
    """

    return bool(
        _DOI_PATTERN.match(
            text.strip(),
        )
    )


def is_isbn(
    text: str,
) -> bool:
    """
    Detect ISBN lines.
    """

    return bool(
        _ISBN_PATTERN.match(
            text.strip(),
        )
    )


def is_short_noise(
    text: str,
    minimum_length: int = 3,
) -> bool:
    """
    Detect extremely short text.
    """

    return len(
        text.strip(),
    ) < minimum_length