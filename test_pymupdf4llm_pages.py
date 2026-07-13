from pathlib import Path

import pymupdf4llm

PDF_PATH = Path(
    "storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf"
)

pages = pymupdf4llm.to_markdown(
    PDF_PATH,
    page_chunks=True,
)

print(type(pages))
print()

print("Pages:", len(pages))
print()

print(type(pages[0]))
print()

print(pages[0].keys())
print()

for key, value in pages[0].items():

    print("=" * 80)
    print(key)

    if isinstance(value, str):

        print(value[:500])

    else:

        print(value)