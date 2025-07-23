import textwrap
from typing import List


def format_comment(text: str) -> str:
    if not text:
        return ""  # pragma: no cover

    if text.startswith("/*") and text.endswith("*/"):
        return text
    lines = text.splitlines()
    return "\n".join(
        line if line.strip().startswith("//") else f"// {line}" for line in lines
    )
