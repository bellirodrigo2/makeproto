from dataclasses import dataclass, fields
from typing import Annotated, get_origin


@dataclass
class Teste:
    one: str
    two: Annotated[str, "foo"]
    three: list[str]


def teste_():
    for f in fields(Teste):
        origin = get_origin(f.type)
        print(f.type, origin)
