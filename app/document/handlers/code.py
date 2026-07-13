from markdown_it.token import Token

from app.document.handlers.base import (
    BaseHandler,
    HandlerResult,
)
from app.document.models import DocumentBlock
from app.enums.block import BlockType


class CodeHandler(BaseHandler):
    """
    Handles fenced code blocks.
    """

    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:

        return (
            tokens[index].type
            == "fence"
        )

    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:

        token = tokens[index]

        block = DocumentBlock(
            text=token.content,
            block_type=BlockType.CODE,
            metadata={
                "language": token.info,
            },
        )

        return HandlerResult(
            block=block,
            next_index=index + 1,
        )