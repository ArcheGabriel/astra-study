from markdown_it.token import Token

from app.document.handlers.base import (
    BaseHandler,
    HandlerResult,
)
from app.document.models import DocumentBlock
from app.document.utils import (
    clean_text,
    is_caption,
)
from app.enums.block import BlockType


class CaptionHandler(BaseHandler):
    """
    Detects figure/table captions.
    """

    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:

        if (
            tokens[index].type
            != "paragraph_open"
        ):
            return False

        if (
            index + 1
            >= len(tokens)
        ):
            return False

        inline = tokens[index + 1]

        return is_caption(
            inline.content,
        )

    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:

        inline = tokens[index + 1]

        block = DocumentBlock(
            text=clean_text(
                inline.content,
            ),
            block_type=BlockType.CAPTION,
        )

        return HandlerResult(
            block=block,
            next_index=index + 3,
        )