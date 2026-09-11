"""Extract all rugby source PDFs into one structured JSON file."""

import json
import re
from pathlib import Path

import fitz

SOURCE_DIR = Path("data/sports/rugby_xv/world_rugby/2026/source")

OUTPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/extracted_documents.json"
)

FILENAME_PATTERN = re.compile(r"^world_rugby_laws_español_(definitions|law(\d+))\.pdf$")


def discover_documents() -> list[tuple[Path, str, int]]:
    """Find and validate the 22 expected source PDFs."""

    documents = []

    for path in SOURCE_DIR.glob("*.pdf"):
        match = FILENAME_PATTERN.match(path.name)

        if not match:
            continue

        document_type = match.group(1)

        if document_type == "definitions":
            number = 0
        else:
            number = int(match.group(2))

        documents.append((path, document_type, number))

    documents.sort(key=lambda item: item[2])

    expected_numbers = list(range(22))
    found_numbers = [item[2] for item in documents]

    if found_numbers != expected_numbers:
        raise ValueError(
            f"Expected definitions + Laws 1-21, " f"but found: {found_numbers}"
        )

    return documents


def extract_pdf(pdf_path: Path) -> list[dict]:
    """Extract every page from one PDF."""

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        pages.append(
            {
                "page": page_number,
                "text": page.get_text("text"),
            }
        )

    document.close()

    return pages


def main() -> None:
    """Extract all source PDFs."""

    documents = discover_documents()

    extracted_documents = []

    total_pages = 0
    empty_pages = 0

    for pdf_path, document_type, number in documents:
        pages = extract_pdf(pdf_path)

        total_pages += len(pages)
        empty_pages += sum(not page["text"].strip() for page in pages)

        extracted_documents.append(
            {
                "type": "definitions" if number == 0 else "law",
                "number": number,
                "source_file": pdf_path.name,
                "pages": pages,
            }
        )

    output = {
        "sport": "rugby",
        "variant": "rugby_xv",
        "source": {
            "organization": "World Rugby",
            "year": 2026,
            "language": "es",
        },
        "documents": extracted_documents,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Documents extracted: {len(documents)}")
    print("Definitions: 1")
    print("Laws extracted: 21")
    print(f"Total pages: {total_pages}")
    print(f"Empty pages: {empty_pages}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
