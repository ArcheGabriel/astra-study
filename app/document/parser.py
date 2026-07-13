from markdown_it import MarkdownIt
from markdown_it.token import Token


class DocumentParser:
    """
    Parses Markdown into Markdown-It tokens.

    This class is intentionally lightweight.

    It does not perform any conversion.
    It only exposes the Markdown AST.
    """

    def __init__(
        self,
    ) -> None:

        self.parser = MarkdownIt(
            "commonmark",
        )

    def parse(
        self,
        markdown: str,
    ) -> list[Token]:
        """
        Parse Markdown into tokens.
        """

        return self.parser.parse(
            markdown,
        )