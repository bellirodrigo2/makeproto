import textwrap
from typing import List


def format_comment(text: str, max_chars: int, always_format: bool) -> str:
    text = text.strip()

    if not text:
        return ""  # pragma: no cover

    if not always_format:
        if text.startswith("//"):
            return text
        if text.startswith("/*") and text.endswith("*/"):
            return text

    text = text.removeprefix("//").strip()
    text = text.removeprefix("/*").strip()
    text = text.removesuffix("*/").strip()

    if len(text) <= max_chars and "\n" not in text:
        return f"// {text}"

    lines: List[str] = textwrap.wrap(text, width=max_chars)
    multiline_comment = "/*\n" + "\n".join(lines) + "\n*/"
    return multiline_comment
