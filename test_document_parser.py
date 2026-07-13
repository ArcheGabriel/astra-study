from pathlib import Path

from app.document.parser import DocumentParser
from app.ingestion.extractors.markdown import MarkdownExtractor

extractor = MarkdownExtractor()

markdown = extractor.extract(
    Path("storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf")
)

parser = DocumentParser()

tokens = parser.parse(markdown)

print(f"Total tokens: {len(tokens)}")

for token in tokens[:20]:
    print(token.type, token.tag)