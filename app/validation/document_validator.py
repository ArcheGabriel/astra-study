from app.chunking.models import DocumentChunk
from app.validation.models import ValidationResult


class DocumentValidator:
    """
    Validates document-level metadata.
    """

    def validate(
        self,
        chunks: list[DocumentChunk],
    ) -> ValidationResult:

        result = ValidationResult(
            name="Document Validator",
            passed=True,
        )

        if not chunks:

            result.passed = False

            result.score = 0.0

            result.warn(
                "No chunks were produced.",
                severity="error",
            )

            return result

        first = chunks[0]

        pages = max(
            chunk.metadata.page_end or 0
            for chunk in chunks
        )

        result.add_metric(
            "Document",
            first.metadata.document_name,
        )

        result.add_metric(
            "Pages",
            pages,
        )

        result.add_metric(
            "Chunks",
            len(chunks),
        )

        result.add_metric(
            "Language",
            first.metadata.language,
        )

        result.add_metric(
            "Checksum",
            first.metadata.checksum,
        )

        result.add_metric(
            "Document UUID",
            first.metadata.document_uuid,
        )

        return result