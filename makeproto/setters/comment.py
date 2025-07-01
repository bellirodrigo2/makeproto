import textwrap
from typing import List

from makeproto.compiler import CompilerPass
from makeproto.template import MethodTemplate, ProtoTemplate, ServiceTemplate


def format_comment(text: str, max_chars: int, always_format: bool) -> str:
    text = text.strip()

    if not text:
        return ""

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


MAXCHAR_PER_LINE = 80
ALWAYS_FORMAT = True


class CommentSetter(CompilerPass):
    def __init__(
        self, maxcharlines: int = MAXCHAR_PER_LINE, always_format: bool = ALWAYS_FORMAT
    ):
        super().__init__()
        self.maxcharlines = maxcharlines
        self.always_format = always_format

    def _format(self, text: str) -> str:
        return format_comment(text, self.maxcharlines, self.always_format)

    def visit_service(self, block: ServiceTemplate) -> None:
        module: ProtoTemplate = self.ctx.get_state(block.module)
        module.comments = self._format(module.comments)
        block.comments = self._format(block.comments)
        for field in block.methods:
            field.accept(self)

    def visit_method(self, method: MethodTemplate) -> None:
        method.comments = self._format(method.comments)
