"""Structure cleaned sports content into laws and regulatory sections."""

import json
import re
from pathlib import Path

INPUT_PATH = Path("data/sports/rugby_xv/world_rugby/2026/structured/cleaned_pages.json")

OUTPUT_PATH = Path(
    "data/sports/rugby_xv/world_rugby/2026/structured/laws_structured.json"
)


LAW_PATTERN = re.compile(r"^Ley\s+(\d+)\s*$", re.IGNORECASE)

SECTION_PATTERN = re.compile(r"^(?P<number>\d+(?:\.\d+)?)\.\s*(?P<title>.+)?$")


def normalize_line(line: str) -> str:
    """Normalize a single line."""

    return re.sub(r"\s+", " ", line).strip()


def is_law_heading(line: str) -> bool:
    """Return True when a line represents a law heading."""

    return LAW_PATTERN.match(line) is not None


def parse_law_number(line: str) -> int:
    """Extract the law number from a law heading."""

    match = LAW_PATTERN.match(line)

    if match is None:
        raise ValueError(f"Invalid law heading: {line}")

    return int(match.group(1))


def is_section_start(line: str) -> bool:
    """Return True when a line starts a numbered regulatory section."""

    return SECTION_PATTERN.match(line) is not None


def parse_section_number(line: str) -> str | None:
    """Extract the section number from a numbered line."""

    match = SECTION_PATTERN.match(line)

    if match is None:
        return None

    return match.group("number")


def merge_wrapped_lines(lines: list[str]) -> str:
    """Merge PDF line wrapping while preserving paragraph boundaries."""

    result = []

    for line in lines:
        line = normalize_line(line)

        if not line:
            if result and result[-1] != "":
                result.append("")
            continue

        if not result or result[-1] == "":
            result.append(line)
            continue

        previous = result[-1]

        # Join normal PDF line wrapping.
        if not previous.endswith((".", ":", ";", "?", "!")):
            result[-1] = f"{previous} {line}"
        else:
            result.append(line)

    return "\n".join(result).strip()


def build_pages_text(pages: list[dict]) -> list[str]:
    """Normalize all page text."""

    return [page["text"] for page in pages if page.get("text", "").strip()]


def extract_laws(pages: list[dict]) -> list[dict]:
    """Extract laws and their numbered sections from page text."""

    laws = []
    current_law = None
    current_section = None
    current_section_lines = []

    def save_section() -> None:
        nonlocal current_section
        nonlocal current_section_lines

        if current_law is None or current_section is None:
            return

        text = merge_wrapped_lines(current_section_lines)

        if text:
            current_law["sections"].append(
                {
                    "number": current_section,
                    "text": text,
                }
            )

        current_section = None
        current_section_lines = []

    def save_law() -> None:
        nonlocal current_law

        save_section()

        if current_law is not None:
            laws.append(current_law)

        current_law = None

    for page in pages:
        page_number = page["page"]

        lines = page["text"].splitlines()

        for raw_line in lines:
            line = normalize_line(raw_line)

            if not line:
                continue

            # Ignore repeated footer.
            if re.match(
                r"^LEYES DEL JUEGO DE RUGBY 2026(?:\s+\d+)?$",
                line,
                re.IGNORECASE,
            ):
                continue

            # Detect "Ley X".
            if is_law_heading(line):
                law_number = parse_law_number(line)

                # If this is the same law we are already processing,
                # it is a repeated page header, not a new law.
                if current_law is not None and current_law["number"] == law_number:
                    if page_number not in current_law["pages"]:
                        current_law["pages"].append(page_number)

                    continue

                # New law.
                save_law()

                current_law = {
                    "number": law_number,
                    "title": "",
                    "pages": [page_number],
                    "sections": [],
                }

                continue

            if current_law is None:
                continue

            if page_number not in current_law["pages"]:
                current_law["pages"].append(page_number)

            # Skip repeated law title if it appears immediately
            # after a repeated "Ley X" header.
            if not current_law["title"]:
                if not is_section_start(line):
                    current_law["title"] = line
                    continue

            # Detect numbered rule/section.
            if is_section_start(line):
                save_section()

                current_section = parse_section_number(line)

                match = SECTION_PATTERN.match(line)

                title_or_text = (
                    match.group("title").strip()
                    if match and match.group("title")
                    else ""
                )

                current_section_lines = []

                if title_or_text:
                    current_section_lines.append(title_or_text)

                continue

            # Continuation of current section.
            if current_section is not None:
                current_section_lines.append(line)

    save_law()

    return laws


def extract_definitions(pages: list[dict]) -> dict:
    """Extract the definitions section before the first law."""

    lines = []

    for page in pages:
        for raw_line in page["text"].splitlines():
            line = normalize_line(raw_line)

            if not line:
                continue

            if is_law_heading(line):
                text = merge_wrapped_lines(lines)

                return {
                    "text": text,
                    "pages": [
                        page_item["page"]
                        for page_item in pages
                        if page_item["page"] < page["page"]
                    ],
                }

            if re.match(
                r"^LEYES DEL JUEGO DE RUGBY 2026(?:\s+\d+)?$",
                line,
                re.IGNORECASE,
            ):
                continue

            lines.append(line)

    return {
        "text": merge_wrapped_lines(lines),
        "pages": [],
    }


def main() -> None:
    """Load cleaned pages and create structured regulatory data."""

    with INPUT_PATH.open("r", encoding="utf-8") as file:
        pages = json.load(file)

    definitions = extract_definitions(pages)
    laws = extract_laws(pages)

    output = {
        "sport": "rugby",
        "variant": "rugby_xv",
        "source": {
            "organization": "World Rugby",
            "year": 2026,
            "language": "es",
        },
        "definitions": definitions,
        "laws": laws,
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

    total_sections = sum(len(law["sections"]) for law in laws)

    print(f"Laws detected: {len(laws)}")
    print(f"Sections detected: {total_sections}")
    print(f"Definitions characters: " f"{len(definitions['text'])}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
