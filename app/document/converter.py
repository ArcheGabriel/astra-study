from markdown_it.token import Token

from app.document.handlers import (
    BaseHandler,
    CaptionHandler,
    CodeHandler,
    FormulaHandler,
    HeadingHandler,
    ImageHandler,
    ListHandler,
    ParagraphHandler,
    TableHandler,
)
from app.document.models import DocumentBlock
from app.document.page import MarkdownPage


class DocumentConverter:
    """
    Converts Markdown-It tokens into semantic DocumentBlocks.

    The converter itself contains no parsing logic.
    All parsing is delegated to registered handlers.

    The converter enriches every block with positional
    information (page number, block index).
    """

    def __init__(
        self,
    ) -> None:

        self.handlers: list[BaseHandler] = [
            HeadingHandler(),
            CaptionHandler(),
            ImageHandler(),
            TableHandler(),
            CodeHandler(),
            FormulaHandler(),
            ListHandler(),
            ParagraphHandler(),
        ]

    def convert(
        self,
        tokens: list[Token],
        page: MarkdownPage,
    ) -> list[DocumentBlock]:
        """
        Convert Markdown tokens into semantic DocumentBlocks.
        """

        blocks: list[DocumentBlock] = []

        token_index = 0

        block_index = 0

        while token_index < len(tokens):

            handled = False

            for handler in self.handlers:

                if not handler.can_handle(
                    tokens,
                    token_index,
                ):
                    continue

                result = handler.handle(
                    tokens,
                    token_index,
                )

                if (
                    result.block is not None
                    and result.block.text.strip()
                ):

                    result.block.page_number = (
                        page.page_number
                    )

                    result.block.block_index = (
                        block_index
                    )

                    blocks.append(
                        result.block,
                    )

                    block_index += 1

                token_index = result.next_index

                handled = True

                break

            if not handled:
                token_index += 1

        return blocks