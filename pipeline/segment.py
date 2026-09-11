"""Create knowledge segments from structured sports documents."""

import json
from pathlib import Path

INPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/structured_documents.json"
)

OUTPUT_PATH = Path("data/sports/rugby_xv/world_rugby/2026/knowledge/segments.json")


def create_segments(documents: list[dict]) -> list[dict]:
    """Convert each numbered law section into one knowledge segment."""

    segments = []

    for document in documents:
        if document["type"] != "law":
            continue

        law_number = document["number"]
        law_title = document["title"]

        for section in document["sections"]:
            text = section["text"].strip()

            if not text:
                continue

            segments.append(
                {
                    "segment_id": (
                        f"rugby_xv_law_" f"{law_number}_section_" f"{section['number']}"
                    ),
                    "sport": "rugby",
                    "variant": "rugby_xv",
                    "source": "World Rugby",
                    "year": 2026,
                    "law_number": law_number,
                    "law_title": law_title,
                    "section_number": section["number"],
                    "heading": section["heading"],
                    "text": text,
                    "source_file": document["source_file"],
                }
            )

    return segments


def main() -> None:
    """Load structured documents and create knowledge segments."""

    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    segments = create_segments(data["documents"])

    output = {
        "sport": data["sport"],
        "variant": data["variant"],
        "source": data["source"],
        "segments": segments,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Segments created: {len(segments)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
