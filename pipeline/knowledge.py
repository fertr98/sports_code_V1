"""Build knowledge units from rugby rule segments."""

import json
from pathlib import Path

INPUT_PATH = Path("data/sports/rugby_xv/world_rugby/2026/knowledge/segments.json")

OUTPUT_PATH = Path("data/sports/rugby_xv/world_rugby/2026/knowledge/knowledge.json")


def build_knowledge_units(segments: list[dict]) -> list[dict]:
    """Convert segments into knowledge units."""

    knowledge_units = []

    for segment in segments:
        knowledge_units.append(
            {
                "knowledge_id": segment["segment_id"],
                "sport": segment["sport"],
                "variant": segment["variant"],
                "source": segment["source"],
                "year": segment["year"],
                "law_number": segment["law_number"],
                "law_title": segment["law_title"],
                "section_number": segment["section_number"],
                "heading": segment["heading"],
                "content": segment["text"],
                "source_file": segment["source_file"],
            }
        )

    return knowledge_units


def main() -> None:
    """Load segments and create knowledge units."""

    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    knowledge_units = build_knowledge_units(data["segments"])

    output = {
        "sport": data["sport"],
        "variant": data["variant"],
        "source": data["source"],
        "knowledge_units": knowledge_units,
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

    print(f"Knowledge units created: " f"{len(knowledge_units)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
