from dataclasses import dataclass, field
from typing import Annotated, List, Optional, Union

import pytest

# Importar as funções e classes que vamos testar
from makeproto.mapclass import NO_DEFAULT, map_class_fields


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
def test_map_class_fields(cls, expected):
    result = map_class_fields(cls)
    assert len(result) == len(expected)

    for res, exp in zip(result, expected):
        name, argtype, basetype, default, has_default, extras = exp

        assert res.name == name
        assert res.argtype == argtype
        assert res.basetype == basetype
        assert res.default == default
        assert res.has_default == has_default
        assert res.extras == extras


# CASO 11: Classe normal com default simples
class ClassSimpleDefault:
    def __init__(self, x: int = 10):
        self.x = x


# CASO 12: Classe normal com múltiplos metadados via Annotated
class ClassAnnotatedMultiple:
    def __init__(self, b: Annotated[str, Meta1(), Meta2()] = "hello"):
        self.b = b


# CASO 13: Classe normal com Optional sem default
class ClassOptionalNoDefault:
    def __init__(self, c: Optional[int]):
        self.c = c


# CASO 14: Classe normal com Union
class ClassWithUnion:
    def __init__(self, f: Union[int, str] = 42):
        self.f = f


# CASO 15: Classe normal com Annotated + Optional
class ClassAnnotatedOptional:
    def __init__(self, e: Annotated[Optional[str], Meta1()] = None):
        self.e = e


@pytest.mark.parametrize(
    "cls, expected",
    [
        (
            ClassSimpleDefault,
            [("x", int, int, 10, True, None)],
        ),
        (
            ClassAnnotatedMultiple,
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
            ClassOptionalNoDefault,
            [("c", Optional[int], Optional[int], NO_DEFAULT, False, None)],
        ),
        (
            ClassWithUnion,
            [("f", Union[int, str], Union[int, str], 42, True, None)],
        ),
        (
            ClassAnnotatedOptional,
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
    ],
)
def test_map_class_fields_regular(cls, expected):
    result = map_class_fields(cls)
    assert len(result) == len(expected)

    for res, exp in zip(result, expected):
        name, argtype, basetype, default, has_default, extras = exp

        assert res.name == name
        assert res.argtype == argtype
        assert res.basetype == basetype
        assert res.default == default
        assert res.has_default == has_default
        assert res.extras == extras


def test_nested_dataclass() -> None:

    @dataclass
    class Base:
        frombase: str

    @dataclass
    class Derived1(Base):
        fromder1: int

    @dataclass
    class Derived2(Derived1):
        fromder2: List[int]

    base_map = map_class_fields(Base)
    assert len(base_map) == 1
    assert base_map[0].name == "frombase"

    der1_map = map_class_fields(Derived1)
    assert len(der1_map) == 2
    assert der1_map[0].name == "frombase"
    assert der1_map[1].name == "fromder1"

    der2_map = map_class_fields(Derived2)
    assert len(der2_map) == 3
    assert der2_map[0].name == "frombase"
    assert der2_map[1].name == "fromder1"
    assert der2_map[2].name == "fromder2"


def test_nested_class() -> None:

    class Base:
        def __init__(self, frombase: str):
            self.frombase = frombase

    class Derived1(Base):
        def __init__(self, frombase: str, fromder1: int):
            self.fromder1 = fromder1
            super().__init__(frombase)

    class Derived2(Derived1):
        def __init__(self, frombase: str, fromder1: int, fromder2: List[int]):
            self.fromder2 = fromder2
            super().__init__(frombase, fromder1)

    base_map = map_class_fields(Base)
    assert len(base_map) == 1
    assert base_map[0].name == "frombase"

    der1_map = map_class_fields(Derived1)
    assert len(der1_map) == 2
    assert der1_map[0].name == "frombase"
    assert der1_map[1].name == "fromder1"

    der2_map = map_class_fields(Derived2)
    assert len(der2_map) == 3
    assert der2_map[0].name == "frombase"
    assert der2_map[1].name == "fromder1"
    assert der2_map[2].name == "fromder2"


# Classes para teste da nova função
class OnlyClassSimple:
    x: int = 10


class OnlyClassAnnotated:
    a: Annotated[int, Meta1()] = 5


class OnlyClassAnnotatedMultiple:
    b: Annotated[str, Meta1(), Meta2()] = "hello"


class OnlyClassOptional:
    c: Optional[int]


class OnlyClassOptionalDefaultNone:
    d: Optional[int] = None


class OnlyClassAnnotatedOptional:
    e: Annotated[Optional[str], Meta1()] = None


class OnlyClassUnion:
    f: Union[int, str] = 42


class OnlyClassNoDefault:
    g: str


class OnlyClassNoHint:
    h = "abc"  # Este campo será ignorado


@pytest.mark.parametrize(
    "cls, expected",
    [
        (
            OnlyClassSimple,
            [("x", int, int, 10, True, None)],
        ),
        (
            OnlyClassAnnotated,
            [("a", Annotated[int, Meta1()], int, 5, True, (Meta1(),))],
        ),
        (
            OnlyClassAnnotatedMultiple,
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
            OnlyClassOptional,
            [("c", Optional[int], Optional[int], NO_DEFAULT, False, None)],
        ),
        (
            OnlyClassOptionalDefaultNone,
            [("d", Optional[int], Optional[int], None, True, None)],
        ),
        (
            OnlyClassAnnotatedOptional,
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
            OnlyClassUnion,
            [("f", Union[int, str], Union[int, str], 42, True, None)],
        ),
        (
            OnlyClassNoDefault,
            [("g", str, str, NO_DEFAULT, False, None)],
        ),
    ],
)
def test_map_class_fields(cls, expected):
    result = map_class_fields(cls)
    assert len(result) == len(expected)

    for res, exp in zip(result, expected):
        name, argtype, basetype, default, has_default, extras = exp

        assert res.name == name
        assert res.argtype == argtype
        assert res.basetype == basetype
        assert res.default == default
        assert res.has_default == has_default
        assert res.extras == extras


class Special:
    @classmethod
    def test(cls) -> str:
        return "foobar"


def test_method() -> None:

    map = map_class_fields(Special)
    assert not map
