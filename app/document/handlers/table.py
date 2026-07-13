from markdown_it.token import Token

from app.document.handlers.base import (
    BaseHandler,
    HandlerResult,
)
from app.document.models import DocumentBlock
from app.document.utils import clean_text
from app.enums.block import BlockType


class TableHandler(BaseHandler):
    """
    Handles Markdown tables.

    Initial implementation stores the textual
    representation. Later we'll preserve the
    complete table structure.
    """

    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:

        return (
            tokens[index].type
            == "table_open"
        )

    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:

        lines: list[str] = []

        i = index + 1

        while i < len(tokens):

            token = tokens[i]

            if token.type == "table_close":
                break

            if token.type == "inline":

                text = clean_text(
                    token.content,
                )

                if text:
                    lines.append(text)

            i += 1

        block = DocumentBlock(
            text="\n".join(lines),
            block_type=BlockType.TABLE,
        )

        return HandlerResult(
            block=block,
            next_index=i + 1,
        )