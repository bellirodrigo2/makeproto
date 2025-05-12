import sys
from dataclasses import dataclass, fields
from enum import Enum
from pathlib import Path
from typing import Any, Optional, get_args, get_origin, get_type_hints

import pytest
from typing_extensions import Annotated

from makeproto.mapclass import map_class_fields
from makeproto.prototypes2 import (
    BaseMessage,
    Bool,
    Bytes,
    Double,
    Fixed32,
    Fixed64,
    Float,
    Int32,
    Int64,
    SInt32,
    SInt64,
    String,
    UInt32,
    UInt64,
)
from makeproto.templates import get_type_str


@dataclass
class StrClass:
    f1: str
    f2: String
    f3: Annotated[str, "foobar"]
    f4: Annotated[String, "foobar"]


@dataclass
class BoolClass:
    f1: bool
    f2: Bool
    f3: Annotated[bool, "foobar"]
    f4: Annotated[Bool, "foobar"]


@dataclass
class BytesClass:
    f1: bytes
    f2: Bytes
    f3: Annotated[bytes, "foobar"]
    f4: Annotated[Bytes, "foobar"]


@dataclass
class FloatClass:
    f1: float
    f2: Float
    f3: Annotated[float, "foobar"]
    f4: Annotated[Float, "foobar"]


@dataclass
class DoubleClass:
    f1: Double
    f4: Annotated[Double, "foobar"]


@dataclass
class IntClass:
    f1: Int32
    f2: Annotated[Int32, "foobar"]
    f3: Int64
    f4: Annotated[Int64, "foobar"]
    f5: UInt32
    f6: Annotated[UInt32, "foobar"]
    f7: UInt64
    f8: Annotated[UInt64, "foobar"]
    f9: SInt32
    f10: Annotated[SInt32, "foobar"]
    f11: SInt64
    f12: Annotated[SInt64, "foobar"]
    f13: Fixed32
    f14: Annotated[Fixed32, "foobar"]
    f15: Fixed64
    f16: Annotated[Fixed64, "foobar"]


class C1(BaseMessage): ...


class C2(BaseMessage): ...


class C3(BaseMessage): ...


@dataclass
class MessageClass:
    f1: C1
    f2: Annotated[C1, "foobar"]
    f3: C2
    f4: Annotated[C2, "foobar"]
    f5: C3
    f6: Annotated[C3, "foobar"]


@pytest.mark.parametrize(
    "class_, str_",
    [
        (StrClass, "string"),
        (BoolClass, "bool"),
        (BytesClass, "bytes"),
        (FloatClass, "float"),
        (DoubleClass, "double"),
    ],
)
def teste_get_type_str(class_: type[Any], str_: str) -> None:

    for f in fields(class_):
        type_str = get_type_str(f.type)
        assert str_ == type_str


def teste_get_type_str_int() -> None:

    for f in fields(IntClass):
        ftype = f.type
        type_str = get_type_str(ftype)
        origin = get_origin(f.type)
        if origin is Annotated:
            ftype = get_args(ftype)[0]
        assert ftype.__name__.lower() == type_str


def teste_get_type_str_message() -> None:

    for f in fields(MessageClass):
        ftype = f.type
        type_str = get_type_str(ftype)
        origin = get_origin(f.type)
        if origin is Annotated:
            ftype = get_args(ftype)[0]
        assert ftype.__name__ == type_str


def teste_type_fail() -> None:
    @dataclass
    class TypeFail:
        f1: Path
        f2: tuple[str, ...]

    for f in fields(TypeFail):
        str_ = get_type_str(f.type)
        assert str_ is None


def teste_list_ok() -> None:

    @dataclass
    class ListClass:
        f1: list[C1]
        f2: Annotated[list[C1], "foobar"]
        f4: Annotated[list[str], "foobar"]
        f6: Annotated[list[Double], "foobar"]

    for f in fields(ListClass):
        ftype = f.type
        origin = get_origin(f.type)
        if origin is Annotated:
            ftype = get_args(ftype)[0]
        type_str = get_type_str(ftype)
        assert type_str.startswith("repeated")


def teste_list_fail() -> None:
    @dataclass
    class MapClass:
        f1: list[Path]
        f2: list[list[str]]
        f3: list[dict[str, str]]
        f4: Annotated[list[Path], "foobar"]
        f5: Annotated[list[list[str]], 123]

    for f in fields(MapClass):
        ftype = f.type
        origin = get_origin(f.type)
        if origin is Annotated:
            ftype = get_args(ftype)[0]
        str_ = get_type_str(ftype)
        assert str_ is None


def teste_map_ok() -> None:

    @dataclass
    class MapClass:
        f1: dict[str, C1]
        f2: Annotated[dict[Int32, int], "foobar"]
        f3: dict[Int32, str]
        f4: Annotated[dict[int, Fixed64], "foobar"]

    for f in fields(MapClass):
        ftype = f.type
        origin = get_origin(f.type)
        if origin is Annotated:
            ftype = get_args(ftype)[0]
        str_ = get_type_str(ftype)
        assert str_.startswith("map<")
        assert str_.endswith(">")


def teste_map_fail() -> None:
    @dataclass
    class MapClass:
        f1: dict[Bytes, C1]
        f2: Annotated[dict[bytes, int], "foobar"]
        f3: dict[list[str], str]
        f4: Annotated[dict[float, Fixed64], "foobar"]
        f5: Annotated[dict[Float, Fixed64], "foobar"]
        f6: Annotated[dict[Double, Fixed64], "foobar"]
        f7: Annotated[dict[list[str], str], "foobar"]
        f8: Annotated[dict[str, Path], "foobar"]
        f9: Annotated[dict[Path, str], "foobar"]

    for f in fields(MapClass):
        ftype = f.type
        origin = get_origin(f.type)
        if origin is Annotated:
            ftype = get_args(ftype)[0]
        str_ = get_type_str(ftype)
        assert str_ is None
