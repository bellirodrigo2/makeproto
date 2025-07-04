from typing import Callable

from makeproto.compiler import CompilerPass
from makeproto.template import MethodTemplate, ServiceTemplate


class NameSetter(CompilerPass):
    def __init__(self, normalize_name: Callable[[str], str] = lambda x: x) -> None:
        super().__init__()
        self.normalize_name = normalize_name

    def visit_service(self, block: ServiceTemplate) -> None:
        block.name = self.normalize_name(block.name)
        for field in block.methods:
            field.accept(self)

    def visit_method(self, method: MethodTemplate) -> None:
        method.name = self.normalize_name(method.name)
