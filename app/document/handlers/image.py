from markdown_it.token import Token

from app.document.handlers.base import (
    BaseHandler,
    HandlerResult,
)
from app.document.models import DocumentBlock
from app.document.utils import (
    clean_text,
    is_image_text,
)
from app.enums.block import BlockType


class ImageHandler(BaseHandler):
    """
    Handles OCR text extracted from figures/images.

    Markdown-based parsers may emit these as HTML blocks or paragraphs
    containing the OCR markers.
    """

    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:

        token = tokens[index]

        if token.type == "html_block":
            return True

        if (
            token.type == "paragraph_open"
            and index + 1 < len(tokens)
        ):
            return is_image_text(
                tokens[index + 1].content,
            )

        return False

    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:

        token = tokens[index]

        if token.type == "html_block":

            text = clean_text(
                token.content,
            )

            if not text:

                return HandlerResult(
                    block=None,
                    next_index=index + 1,
                )

            block = DocumentBlock(
                text=text,
                block_type=BlockType.IMAGE_TEXT,
            )

            return HandlerResult(
                block=block,
                next_index=index + 1,
            )

        inline = tokens[index + 1]

        text = clean_text(
            inline.content,
        )

        if not text:

            return HandlerResult(
                block=None,
                next_index=index + 3,
            )

        block = DocumentBlock(
            text=text,
            block_type=BlockType.IMAGE_TEXT,
        )

        return HandlerResult(
            block=block,
            next_index=index + 3,
        )
