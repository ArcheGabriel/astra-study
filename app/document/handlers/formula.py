from markdown_it.token import Token

from app.document.handlers.base import (
    BaseHandler,
    HandlerResult,
)
from app.document.models import DocumentBlock
from app.enums.block import BlockType


class FormulaHandler(BaseHandler):
    """
    Placeholder for mathematical expressions.

    PyMuPDF4LLM currently emits most formulas as text.
    This handler prepares the pipeline for future
    LaTeX/MathML support.
    """

    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:

        token = tokens[index]

        return token.type in (
            "math_block",
            "display_math",
        )

    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:

        token = tokens[index]

        block = DocumentBlock(
            text=token.content,
            block_type=BlockType.FORMULA,
        )

        return HandlerResult(
            block=block,
            next_index=index + 1,
        )