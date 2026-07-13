from dataclasses import dataclass


@dataclass(slots=True)
class ChunkingConfig:
    """
    Configuration shared by the chunking pipeline.
    """

    # Preferred chunk size.
    target_size: int = 3000

    # Maximum chunk size before forcing a split.
    max_size: int = 3800

    # Number of overlapping characters.
    overlap: int = 300

    # Recursive split order.
    separators: tuple[str, ...] = (
        "\n\n",
        "\n•",
        "\n-",
        ". ",
        " ",
    )