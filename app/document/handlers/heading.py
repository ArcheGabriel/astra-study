from markdown_it.token import Token

from app.document.handlers.base import (
    BaseHandler,
    HandlerResult,
)
from app.document.models import DocumentBlock
from app.document.utils import clean_text
from app.enums.block import BlockType


class HeadingHandler(BaseHandler):
    """
    Handles Markdown headings.
    """

    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:

        return (
            tokens[index].type == "heading_open"
        )

    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:

        opening = tokens[index]
        inline = tokens[index + 1]

        level = int(
            opening.tag.replace(
                "h",
                "",
            )
        )

        text = clean_text(
            inline.content,
        )

        block = DocumentBlock(
            text=text,
            block_type=BlockType.HEADING,
            level=level,
        )

        return HandlerResult(
            block=block,
            next_index=index + 3,
        )