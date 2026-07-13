from markdown_it.token import Token

from app.document.handlers.base import (
    BaseHandler,
    HandlerResult,
)
from app.document.models import DocumentBlock
from app.document.utils import clean_text
from app.enums.block import BlockType


class ListHandler(BaseHandler):
    """
    Handles unordered and ordered lists.
    """

    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:

        return (
            tokens[index].type
            in (
                "bullet_list_open",
                "ordered_list_open",
            )
        )

    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:

        lines: list[str] = []

        i = index + 1

        while (
            i < len(tokens)
        ):

            token = tokens[i]

            if (
                token.type
                in (
                    "bullet_list_close",
                    "ordered_list_close",
                )
            ):
                break

            if token.type == "inline":

                text = clean_text(
                    token.content,
                )

                if text:
                    lines.append(text)

            i += 1

        block = DocumentBlock(
            text="\n".join(
                lines,
            ),
            block_type=BlockType.LIST,
        )

        return HandlerResult(
            block=block,
            next_index=i + 1,
        )