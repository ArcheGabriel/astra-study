from pathlib import Path

from app.ingestion.extractors.markdown import MarkdownExtractor


extractor = MarkdownExtractor()

markdown = extractor.extract(
    Path("storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf"),
)

print(markdown[:5000])