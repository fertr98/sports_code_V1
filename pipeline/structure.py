"""Structure cleaned sports documents into sections."""

import json
import re
from pathlib import Path

INPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/cleaned_documents.json"
)

OUTPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/structured_documents.json"
)


HEADER_PATTERNS = [
    re.compile(r"^WORLDRUGBY$", re.IGNORECASE),
    re.compile(r"^LEYES DEL JUEGO DE RUGBY 2026(?:\s+\d+)?$", re.IGNORECASE),
]


def is_section_start(line: str) -> bool:
    """Detect numbered law sections."""

    return bool(
        re.match(
            r"^\d+\.\s*",
            line.strip(),
        )
    )


def is_all_caps_heading(line: str) -> bool:
    """Detect standalone uppercase headings."""

    line = line.strip()

    if not line:
        return False

    if any(pattern.match(line) for pattern in HEADER_PATTERNS):
        return False

    if len(line.split()) > 15:
        return False

    letters = [char for char in line if char.isalpha()]

    if not letters:
        return False

    return all(char.isupper() for char in letters)


def is_title_heading(line: str) -> bool:
    """Detect short title-style headings."""

    line = line.strip()

    if not line:
        return False

    if len(line.split()) > 6:
        return False

    if line[-1:] in ".,:;!?":
        return False

    if any(char.isdigit() for char in line):
        return False

    words = line.split()

    if len(words) < 2:
        return False

    # Normal sentences are not headings.
    forbidden_starts = {
        "Antes",
        "Después",
        "Cuando",
        "Si",
        "Los",
        "Las",
        "El",
        "La",
        "Un",
        "Una",
        "Cada",
        "Ningún",
        "Ninguna",
        "Cualquier",
        "Todo",
        "Toda",
        "En",
        "Para",
        "Por",
        "Durante",
    }

    if words[0] in forbidden_starts:
        return False

    return words[0][0].isupper()


def is_heading(line: str) -> bool:
    """Detect likely real headings."""

    return is_all_caps_heading(line) or is_title_heading(line)


def remove_artifacts(lines: list[str]) -> list[str]:
    """Remove repeated PDF headers and footers."""

    cleaned = []

    for line in lines:
        line = line.strip()

        if any(pattern.match(line) for pattern in HEADER_PATTERNS):
            continue

        cleaned.append(line)

    return cleaned


def extract_sections(text: str) -> list[dict]:
    """Extract every numbered section."""

    lines = remove_artifacts(text.splitlines())

    sections = []
    current_section = None

    for line in lines:
        line = line.strip()

        if is_section_start(line):
            if current_section is not None:
                sections.append(current_section)

            match = re.match(
                r"^(\d+)\.\s*(.*)$",
                line,
            )

            number = int(match.group(1))
            remainder = match.group(2).strip()

            current_section = {
                "number": number,
                "heading": "",
                "text_lines": [],
            }

            # Important:
            # the text after "10." is NOT automatically a heading.
            if remainder:
                current_section["text_lines"].append(remainder)

            continue

        if current_section is None:
            continue

        current_section["text_lines"].append(line)

    if current_section is not None:
        sections.append(current_section)

    return sections


def move_headings_to_next_section(
    sections: list[dict],
) -> list[dict]:
    """
    Detect headings that appear immediately before the next
    numbered section because of PDF extraction order.
    """

    for index in range(len(sections) - 1):
        current = sections[index]
        next_section = sections[index + 1]

        lines = current["text_lines"]

        while lines and not lines[-1]:
            lines.pop()

        if not lines:
            continue

        candidate = lines[-1]

        if is_heading(candidate):
            next_section["heading"] = candidate
            lines.pop()

    return sections


def clean_section_text(sections: list[dict]) -> list[dict]:
    """Clean section text and preserve all regulatory content."""

    result = []

    for section in sections:
        lines = section["text_lines"]

        while lines and not lines[0]:
            lines.pop(0)

        while lines and not lines[-1]:
            lines.pop()

        result.append(
            {
                "number": section["number"],
                "heading": section["heading"],
                "text": "\n".join(lines),
            }
        )

    return result


def structure_document(document: dict) -> dict:
    """Structure one document."""

    if document["type"] == "definitions":
        return {
            "type": "definitions",
            "number": 0,
            "title": "Definiciones",
            "source_file": document["source_file"],
            "text": "\n\n".join(
                page["text"] for page in document["pages"] if page["text"].strip()
            ),
            "sections": [],
        }

    full_text = "\n".join(
        page["text"] for page in document["pages"] if page["text"].strip()
    )

    sections = extract_sections(full_text)
    sections = move_headings_to_next_section(sections)
    sections = clean_section_text(sections)

    return {
        "type": "law",
        "number": document["number"],
        "title": "",
        "source_file": document["source_file"],
        "text": full_text,
        "sections": sections,
    }


def main() -> None:
    """Create structured documents."""

    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    structured_documents = [
        structure_document(document) for document in data["documents"]
    ]

    output = {
        "sport": data["sport"],
        "variant": data["variant"],
        "source": data["source"],
        "documents": structured_documents,
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

    laws = [document for document in structured_documents if document["type"] == "law"]

    total_sections = sum(len(law["sections"]) for law in laws)

    print(f"Documents structured: " f"{len(structured_documents)}")
    print(f"Laws structured: " f"{len(laws)}")
    print(f"Total sections: " f"{total_sections}")

    for law in laws:
        print(
            f"Law {law['number']}: "
            f"{law['title']} "
            f"({len(law['sections'])} sections)"
        )

    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
