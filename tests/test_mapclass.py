from dataclasses import dataclass, field
from typing import Annotated, List, Optional, Union

import pytest

# Importar as funções e classes que vamos testar
from makeproto.mapclass import NO_DEFAULT, get_dataclass_fields


# Tipos auxiliares para metadados em Annotated
@dataclass(frozen=True)
class Meta1:
    pass


@dataclass(frozen=True)
class Meta2:
    pass


# CASO 1: Campo com default simples
@dataclass
class SimpleDefault:
    x: int = 10


# CASO 2: Campo com default_factory
@dataclass
class WithDefaultFactory:
    y: List[int] = field(default_factory=list)


# CASO 3: Campo sem default
@dataclass
class NoDefault:
    z: str


# CASO 4: Annotated simples com um metadado
@dataclass
class AnnotatedSingle:
    a: Annotated[int, Meta1()] = 5


# CASO 5: Annotated com múltiplos metadados
@dataclass
class AnnotatedMultiple:
    b: Annotated[str, Meta1(), Meta2()] = "hello"


# CASO 6: Optional sem default
@dataclass
class OptionalNoDefault:
    c: Optional[int]


# CASO 7: Optional com default None
@dataclass
class OptionalDefaultNone:
    d: Optional[int] = None


# CASO 8: Annotated + Optional
@dataclass
class AnnotatedOptional:
    e: Annotated[Optional[str], Meta1()] = None


# CASO 9: Union
@dataclass
class WithUnion:
    f: Union[int, str] = 42


# CASO 10: Campo sem hint
@dataclass
class NoHint:
    g = "abc"


@pytest.mark.parametrize(
    "cls, expected",
    [
        (
            SimpleDefault,
            [("x", int, int, 10, True, None)],
        ),
        (
            WithDefaultFactory,
            [("y", List[int], List[int], list, True, None)],
        ),
        (
            NoDefault,
            [("z", str, str, NO_DEFAULT, False, None)],
        ),
        (
            AnnotatedSingle,
            [("a", Annotated[int, Meta1()], int, 5, True, (Meta1(),))],
        ),
        (
            AnnotatedMultiple,
            [
                (
                    "b",
                    Annotated[str, Meta1(), Meta2()],
                    str,
                    "hello",
                    True,
                    (Meta1(), Meta2()),
                )
            ],
        ),
        (
            OptionalNoDefault,
            [("c", Optional[int], Optional[int], NO_DEFAULT, False, None)],
        ),
        (
            OptionalDefaultNone,
            [("d", Optional[int], Optional[int], None, True, None)],
        ),
        (
            AnnotatedOptional,
            [
                (
                    "e",
                    Annotated[Optional[str], Meta1()],
                    Optional[str],
                    None,
                    True,
                    (Meta1(),),
                )
            ],
        ),
        (
            WithUnion,
            [("f", Union[int, str], Union[int, str], 42, True, None)],
        ),
        # (
        # NoHint,
        # [("g", str, str, "abc", True, None)],
        # ),
    ],
)
def test_get_dataclass_fields(cls, expected):
    result = get_dataclass_fields(cls)
    assert len(result) == len(expected)

    for res, exp in zip(result, expected):
        name, argtype, basetype, default, has_default, extras = exp

        assert res.name == name
        assert res.argtype == argtype
        assert res.basetype == basetype
        assert res.default == default
        assert res.has_default == has_default
        assert res.extras == extras
