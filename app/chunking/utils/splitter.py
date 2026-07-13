import re

from nltk.tokenize import sent_tokenize

from app.chunking.utils.tokens import (
    count_tokens,
    detokenize,
    join_sentences,
    tokenize,
)

DEFAULT_MODEL = "text-embedding-3-large"

_PARAGRAPH_PATTERN = re.compile(
    r"\n\s*\n+",
)


def split_paragraphs(
    text: str,
) -> list[str]:

    text = text.strip()

    if not text:
        return []

    paragraphs = [

        paragraph.strip()

        for paragraph in _PARAGRAPH_PATTERN.split(
            text,
        )

        if paragraph.strip()

    ]

    return paragraphs or [text]


def split_sentences(
    paragraph: str,
) -> list[str]:

    paragraph = paragraph.strip()

    if not paragraph:
        return []

    return sent_tokenize(
        paragraph,
    )


def split_long_sentence(
    sentence: str,
    max_tokens: int,
    model: str = DEFAULT_MODEL,
) -> list[str]:
    """
    Split one oversized sentence into pieces that are
    guaranteed to fit within max_tokens after
    detokenization and re-encoding.

    tiktoken.decode() is not perfectly reversible:
    decoding 700 token ids can sometimes re-encode
    to 704–710 tokens because of whitespace merging.

    Therefore every emitted piece is validated by
    re-encoding before being returned.
    """

    token_ids = tokenize(
        sentence,
        model,
    )

    if len(token_ids) <= max_tokens:

        return [
            sentence,
        ]

    pieces: list[str] = []

    start = 0

    while start < len(token_ids):

        end = min(
            start + max_tokens,
            len(token_ids),
        )

        #
        # Build candidate piece.
        #
        text = detokenize(
            token_ids[start:end],
            model,
        )

        #
        # Validate after decoding.
        #
        while (

            end > start

            and count_tokens(
                text,
                model,
            ) > max_tokens

        ):

            end -= 1

            text = detokenize(
                token_ids[start:end],
                model,
            )

        #
        # Safety fallback.
        #
        if end == start:

            end = start + 1

            text = detokenize(
                token_ids[start:end],
                model,
            )

        pieces.append(
            text,
        )

        start = end

    return pieces


def flatten_sentences(
    paragraphs: list[str],
    max_tokens: int,
    model: str = DEFAULT_MODEL,
) -> list[str]:

    flattened: list[str] = []

    for paragraph in paragraphs:

        sentences = split_sentences(
            paragraph,
        )

        for sentence in sentences:

            flattened.extend(

                split_long_sentence(
                    sentence,
                    max_tokens,
                    model,
                )

            )

    return flattened


def _serialized_tokens(
    sentences: list[str],
    model: str,
) -> int:
    """
    Count tokens after serialization exactly as the
    chunk will be emitted.
    """

    return count_tokens(
        join_sentences(sentences),
        model,
    )


def build_windows(
    sentences: list[str],
    max_tokens: int,
    overlap_tokens: int,
    model: str = DEFAULT_MODEL,
) -> list[list[str]]:

    if not sentences:
        return []

    windows: list[list[str]] = []

    current_window: list[str] = []

    index = 0

    while index < len(sentences):

        candidate = current_window + [
            sentences[index]
        ]

        #
        # IMPORTANT
        #
        # Validate using the FINAL serialized text,
        # not by summing sentence token counts.
        #
        if (
            _serialized_tokens(
                candidate,
                model,
            )
            <= max_tokens
        ):

            current_window = candidate

            index += 1

            continue

        #
        # Save finished window.
        #
        if current_window:

            windows.append(
                current_window,
            )

        #
        # Build overlap.
        #
        overlap: list[str] = []

        for sentence in reversed(
            current_window,
        ):

            trial = [
                sentence,
                *overlap,
            ]

            if (
                _serialized_tokens(
                    trial,
                    model,
                )
                > overlap_tokens
            ):
                break

            overlap = trial

        current_window = overlap

        #
        # Prevent infinite loop if the overlap
        # alone consumes the budget.
        #
        while (

            current_window

            and _serialized_tokens(
                current_window
                + [sentences[index]],
                model,
            )
            > max_tokens

        ):

            current_window.pop(0)

    if current_window:

        windows.append(
            current_window,
        )

    #
    # Final defensive validation.
    #
    validated: list[list[str]] = []

    for window in windows:

        working = list(window)

        while (

            working

            and _serialized_tokens(
                working,
                model,
            )
            > max_tokens

        ):

            working.pop()

        if working:

            validated.append(
                working,
            )

    return validated


def split_for_embeddings(
    text: str,
    max_tokens: int,
    overlap_tokens: int,
    model: str = DEFAULT_MODEL,
) -> list[list[str]]:

    paragraphs = split_paragraphs(
        text,
    )

    sentences = flatten_sentences(
        paragraphs,
        max_tokens,
        model,
    )

    return build_windows(
        sentences,
        max_tokens,
        overlap_tokens,
        model,
    )