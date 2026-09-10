"""Extract raw sports content into the source data directory."""

import json
from pathlib import Path
import fitz

PDF_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/source/world_rugby_laws_español_repaired.pdf"
)

OUTPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/extracted_pages.json"
)


def extract_pages(pdf_path: Path) -> list[dict]:
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
    pages = extract_pages(PDF_PATH)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            pages,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Extracted {len(pages)} pages.")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
