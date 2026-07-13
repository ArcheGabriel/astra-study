from collections import Counter
from pathlib import Path

from app.document.converter import DocumentConverter
from app.document.parser import DocumentParser
from app.ingestion.extractors.markdown import MarkdownExtractor


PDF_PATH = Path(
    "storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf"
)


def main():

    print("=" * 80)
    print("DOCUMENT PIPELINE TEST")
    print("=" * 80)

    extractor = MarkdownExtractor()

    pages = extractor.extract(
        PDF_PATH,
    )

    print()

    print(
        f"Pages : {len(pages)}"
    )

    parser = DocumentParser()

    converter = DocumentConverter()

    blocks = []

    for page in pages:

        tokens = parser.parse(
            page.markdown,
        )

        page_blocks = converter.convert(
            tokens,
            page,
        )

        blocks.extend(
            page_blocks,
        )

    print(
        f"Blocks : {len(blocks):,}"
    )

    print()

    print("=" * 80)
    print("BLOCK TYPE DISTRIBUTION")
    print("=" * 80)

    counter = Counter(
        block.block_type
        for block in blocks
    )

    for block_type, count in sorted(
        counter.items(),
        key=lambda x: x[0],
    ):

        print(
            f"{block_type:<15} : {count}"
        )

    print()

    print("=" * 80)
    print("FIRST 25 BLOCKS")
    print("=" * 80)

    for i, block in enumerate(
        blocks[:25]
    ):

        print()

        print("-" * 60)

        print(
            f"Block #{i}"
        )

        print(
            f"Type  : {block.block_type}"
        )

        print(
            f"Level : {block.level}"
        )

        print(
            f"Page  : {block.page_number}"
        )

        print(
            f"Block : {block.block_index}"
        )

        print()

        print(
            block.text[:250]
        )

    print()

    print("=" * 80)
    print("QUALITY CHECK")
    print("=" * 80)

    empty = sum(
        not block.text.strip()
        for block in blocks
    )

    duplicates = len(blocks) - len(
        {
            (
                block.page_number,
                block.block_index,
                block.block_type,
                block.text,
            )
            for block in blocks
        }
    )

    longest_block = max(
        blocks,
        key=lambda b: len(
            b.text,
        ),
    )

    average = (
        sum(
            len(
                block.text,
            )
            for block in blocks
        )
        / len(blocks)
    )

    print()

    print(
        f"Empty Blocks      : {empty}"
    )

    print(
        f"Duplicate Blocks  : {duplicates}"
    )

    print(
        f"Average Length    : {average:.2f}"
    )

    print(
        f"Longest Block     : {len(longest_block.text)}"
    )

    print(
        f"Longest Type      : {longest_block.block_type}"
    )

    print(
        f"Longest Page      : {longest_block.page_number}"
    )

    print(
        f"Longest Index     : {longest_block.block_index}"
    )

    print()

    print("=" * 80)
    print("LONGEST BLOCK PREVIEW")
    print("=" * 80)

    print(
        longest_block.text[:500]
    )


if __name__ == "__main__":
    main()