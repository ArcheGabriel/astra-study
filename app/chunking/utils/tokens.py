from functools import lru_cache

import tiktoken


DEFAULT_MODEL = "text-embedding-3-large"


@lru_cache(maxsize=8)
def get_encoding(
    model: str = DEFAULT_MODEL,
):
    """
    Return and cache the tokenizer for a model.

    Tokenizers are expensive to construct, so we keep
    one cached instance per model.
    """

    return tiktoken.encoding_for_model(
        model,
    )


def count_tokens(
    text: str,
    model: str = DEFAULT_MODEL,
) -> int:
    """
    Count the number of tokens in text.
    """

    if not text:
        return 0

    encoding = get_encoding(
        model,
    )

    return len(
        encoding.encode(
            text,
        )
    )


def truncate_to_tokens(
    text: str,
    max_tokens: int,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Truncate text to a maximum token count.
    """

    if not text:
        return ""

    encoding = get_encoding(
        model,
    )

    tokens = encoding.encode(
        text,
    )

    tokens = tokens[:max_tokens]

    return encoding.decode(
        tokens,
    )


def tokenize(
    text: str,
    model: str = DEFAULT_MODEL,
) -> list[int]:
    """
    Encode text into token ids.
    """

    if not text:
        return []

    return get_encoding(
        model,
    ).encode(
        text,
    )


def detokenize(
    tokens: list[int],
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Decode token ids back into text.
    """

    if not tokens:
        return ""

    return get_encoding(
        model,
    ).decode(
        tokens,
    )


def join_sentences(
    sentences: list[str],
) -> str:
    """
    Join multiple sentences into a single block
    while removing unnecessary whitespace.
    """

    return " ".join(

        sentence.strip()

        for sentence in sentences

        if sentence.strip()

    )