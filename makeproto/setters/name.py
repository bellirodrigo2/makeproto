# --------- Name Normalizer ------------------


import re
from enum import Enum, auto
from typing import Callable, Dict

from makeproto.compiler import CompilerPass
from makeproto.template import MethodTemplate, ServiceTemplate


class NameTransformStrategy(Enum):
    NO_TRANSFORM = auto()
    SNAKE_CASE = auto()
    CAMEL_CASE = auto()
    PASCAL_CASE = auto()


def to_snake_case(name: str) -> str:

    name = re.sub(r"[\-\s]+", "_", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"__+", "_", name)
    return name.lower()


def to_camel_case(name: str) -> str:
    # quebra por underscore, hífen ou espaço
    parts = re.split(r"[_\-\s]+", name)
    if not parts:
        return ""
    # força só a primeira letra da primeira parte a minúscula
    first = parts[0]
    first = first[0].lower() + first[1:] if first else ""
    # capitaliza cada parte subsequente
    rest = "".join(word.capitalize() for word in parts[1:])
    return first + rest


def to_pascal_case(name: str) -> str:
    parts = re.split(r"[_\-\s]+", name)
    return "".join(word.capitalize() for word in parts)


name_strategy: Dict[NameTransformStrategy, Callable[[str], str]] = {
    NameTransformStrategy.SNAKE_CASE: to_snake_case,
    NameTransformStrategy.CAMEL_CASE: to_camel_case,
    NameTransformStrategy.PASCAL_CASE: to_pascal_case,
}


def normalize_name(name: str, strategy: NameTransformStrategy) -> str:
    transform = name_strategy.get(strategy, lambda x: x)
    return transform(name)


def set_name_case_strategy(strategy: str) -> NameTransformStrategy:
    strategy = (
        strategy.strip().replace(" ", "").replace("_", "").replace("-", "").lower()
    )
    # if strategy == "snakecase":
    if "snake" in strategy:
        return NameTransformStrategy.SNAKE_CASE
    # if strategy == "camelcase":
    if "camel" in strategy:
        return NameTransformStrategy.CAMEL_CASE
    # if strategy == "pascalcase":
    if "pascal" in strategy:
        return NameTransformStrategy.PASCAL_CASE
    return NameTransformStrategy.NO_TRANSFORM


DEFAULT_CASE = "no_transform"


class NameSetter(CompilerPass):
    def __init__(self, strategy: str = DEFAULT_CASE) -> None:
        super().__init__()
        self.strategy = set_name_case_strategy(strategy)

    def visit_service(self, block: ServiceTemplate) -> None:
        block.name = normalize_name(block.name, self.strategy)
        for field in block.methods:
            field.accept(self)

    def visit_method(self, method: MethodTemplate) -> None:
        method.name = normalize_name(method.name, self.strategy)
