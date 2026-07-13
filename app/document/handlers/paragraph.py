from markdown_it.token import Token

from app.document.handlers.base import (
    BaseHandler,
    HandlerResult,
)
from app.document.models import DocumentBlock
from app.document.utils import (
    clean_text,
    is_page_number,
)
from app.enums.block import BlockType


class ParagraphHandler(BaseHandler):
    """
    Default handler for normal paragraphs.

    This handler MUST always be the last one
    registered in the converter.
    """

    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:

        return (
            tokens[index].type
            == "paragraph_open"
        )

    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:

        inline = tokens[index + 1]

        text = clean_text(
            inline.content,
        )

        if not text:

            return HandlerResult(
                block=None,
                next_index=index + 3,
            )

        block_type = (
            BlockType.PAGE_NUMBER
            if is_page_number(
                text,
            )
            else BlockType.TEXT
        )

        block = DocumentBlock(
            text=text,
            block_type=block_type,
        )

        return HandlerResult(
            block=block,
            next_index=index + 3,
        )