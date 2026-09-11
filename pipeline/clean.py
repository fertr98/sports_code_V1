"""Clean extracted sports documents without losing regulatory information."""

import json
import re
from pathlib import Path

INPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/extracted_documents.json"
)

OUTPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/cleaned_documents.json"
)


def normalize_text(text: str) -> str:
    """Normalize extracted PDF text while preserving meaningful content."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = "".join(
        char for char in text if char == "\n" or char == "\t" or char.isprintable()
    )

    text = text.replace("\u00a0", " ")
    text = text.replace("\u2007", " ")
    text = text.replace("\u202f", " ")

    lines = [line.rstrip() for line in text.split("\n")]

    cleaned_lines = []

    for line in lines:
        line = re.sub(r"[ \t]+", " ", line)
        cleaned_lines.append(line.strip())

    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    cleaned_text = re.sub(r"\s+([,.;:!?])", r"\1", cleaned_text)

    return cleaned_text.strip()


def clean_documents(documents: list[dict]) -> list[dict]:
    """Clean every page while preserving document boundaries."""

    cleaned_documents = []

    for document in documents:
        cleaned_pages = []

        for page in document["pages"]:
            cleaned_pages.append(
                {
                    "page": page["page"],
                    "text": normalize_text(page["text"]),
                }
            )

        cleaned_documents.append(
            {
                "type": document["type"],
                "number": document["number"],
                "source_file": document["source_file"],
                "pages": cleaned_pages,
            }
        )

    return cleaned_documents


def main() -> None:
    """Load, clean and save all extracted documents."""

    with INPUT_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    cleaned_documents = clean_documents(data["documents"])

    output = {
        "sport": data["sport"],
        "variant": data["variant"],
        "source": data["source"],
        "documents": cleaned_documents,
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

    total_pages = sum(len(document["pages"]) for document in cleaned_documents)

    empty_pages = sum(
        not page["text"] for document in cleaned_documents for page in document["pages"]
    )

    total_chars = sum(
        len(page["text"])
        for document in cleaned_documents
        for page in document["pages"]
    )

    print(f"Documents cleaned: {len(cleaned_documents)}")
    print(f"Total pages: {total_pages}")
    print(f"Empty pages: {empty_pages}")
    print(f"Total characters: {total_chars}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
