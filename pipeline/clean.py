"""Clean extracted sports content without losing regulatory information."""

import json
import re
from pathlib import Path

INPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/extracted_pages.json"
)

OUTPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/cleaned_pages.json"
)


def normalize_text(text: str) -> str:
    """Normalize extracted PDF text while preserving meaningful content."""

    # Normalize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable control characters except newline and tab.
    text = "".join(
        char for char in text if char == "\n" or char == "\t" or char.isprintable()
    )

    # Normalize non-breaking spaces and similar whitespace.
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2007", " ")
    text = text.replace("\u202f", " ")

    # Remove trailing whitespace from every line.
    lines = [line.rstrip() for line in text.split("\n")]

    # Collapse multiple spaces/tabs inside lines.
    cleaned_lines = []

    for line in lines:
        line = re.sub(r"[ \t]+", " ", line)
        cleaned_lines.append(line.strip())

    # Remove repeated blank lines.
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    # Remove spaces before punctuation.
    cleaned_text = re.sub(r"\s+([,.;:!?])", r"\1", cleaned_text)

    return cleaned_text.strip()


def clean_pages(pages: list[dict]) -> list[dict]:
    """Clean the text of every extracted page."""

    cleaned_pages = []

    for page in pages:
        cleaned_pages.append(
            {
                "page": page["page"],
                "text": normalize_text(page["text"]),
            }
        )

    return cleaned_pages


def main() -> None:
    """Load extracted pages, clean them and save the result."""

    with INPUT_PATH.open("r", encoding="utf-8") as file:
        pages = json.load(file)

    cleaned_pages = clean_pages(pages)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            cleaned_pages,
            file,
            ensure_ascii=False,
            indent=2,
        )

    total_chars = sum(len(page["text"]) for page in cleaned_pages)
    empty_pages = sum(not page["text"] for page in cleaned_pages)

    print(f"Cleaned {len(cleaned_pages)} pages.")
    print(f"Empty pages: {empty_pages}")
    print(f"Total characters: {total_chars}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
