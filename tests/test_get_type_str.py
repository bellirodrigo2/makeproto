from dataclasses import dataclass, fields
from pathlib import Path
from typing import Annotated, get_args, get_origin

import pytest

from makeproto.builder.make_msg import get_type_str
from makeproto.prototypes import (
    BaseMessage,
    Bool,
    Bytes,
    Double,
    Enum,
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


def teste_str():

    @dataclass
    class StrClass:
        f1: str
        f2: String
        f3: Annotated[str, "foobar"]
        f4: Annotated[String, "foobar"]

    for f in fields(StrClass):
        str_ = get_type_str(f.type)
        assert str_ == "string"


def teste_bool():

    @dataclass
    class BoolClass:
        f1: bool
        f2: Bool
        f3: Annotated[bool, "foobar"]
        f4: Annotated[Bool, "foobar"]

    for f in fields(BoolClass):
        str_ = get_type_str(f.type)
        assert str_ == "bool"


def teste_bytes():

    @dataclass
    class BytesClass:
        f1: bytes
        f2: Bytes
        f3: Annotated[bytes, "foobar"]
        f4: Annotated[Bytes, "foobar"]

    for f in fields(BytesClass):
        str_ = get_type_str(f.type)
        assert str_ == "bytes"


def teste_float():

    @dataclass
    class FloatClass:
        f1: float
        f2: Float
        f3: Annotated[float, "foobar"]
        f4: Annotated[Float, "foobar"]

    for f in fields(FloatClass):
        str_ = get_type_str(f.type)
        assert str_ == "float"


def teste_double():

    @dataclass
    class DoubleClass:
        f1: Double
        f4: Annotated[Double, "foobar"]

    for f in fields(DoubleClass):
        str_ = get_type_str(f.type)
        assert str_ == "double"


def teste_int():

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

    for f in fields(class_or_instance=IntClass):
        str_ = get_type_str(f.type)
        if get_origin(f.type) is Annotated:
            args = get_args(f.type)
            type_ = args[0].prototype()
        else:
            type_ = f.type.prototype()
        assert str_ == type_

def teste_type_fail():

    @dataclass
    class TypeFail:
        f1: Path
        f2: tuple[str,...]

    for f in fields(TypeFail):
        with pytest.raises(ValueError): 
            get_type_str(f.type, True)


def teste_message():

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
        f7: Enum
        f8: Annotated[Enum, "foobar"]

    for f in fields(class_or_instance=MessageClass):
        str_ = get_type_str(f.type)
        if get_origin(f.type) is Annotated:
            args = get_args(f.type)
            type_ = args[0].prototype()
        else:
            type_ = f.type.prototype()
        assert str_ == type_


def teste_list_ok():

    @dataclass
    class ListClass:
        f1: list[C1]
        f2: Annotated[list[C1], "foobar"]
        f3: set[str]
        f4: Annotated[list[str], "foobar"]
        f5: set[Int32]
        f6: Annotated[list[Double], "foobar"]
        f7: list[Enum]
        f8: Annotated[list[Enum], "foobar"]

    for f in fields(class_or_instance=ListClass):
        str_ = get_type_str(f.type)
        assert str_.startswith("repeated")

def teste_list_fail():
    @dataclass
    class MapClass:
        f1: list[Path]
        f2: list[list[str]]
        f3: list[dict[str,str]]
        f4: Annotated[list[Path], 'foobar']
        f5: Annotated[list[list[str]],123]

    for f in fields(class_or_instance=MapClass):
        with pytest.raises(ValueError):        
            get_type_str(f.type)


class C1(BaseMessage): ...

def teste_map_ok():

    @dataclass
    class MapClass:
        f1: dict[str, C1]
        f2: Annotated[dict[Int32, int], "foobar"]
        f3: dict[Int32, str]
        f4: Annotated[dict[int, Fixed64], "foobar"]

    for f in fields(class_or_instance=MapClass):
        str_ = get_type_str(f.type)
        assert str_.startswith("map<")
        assert str_.endswith(">")

def teste_map_fail():
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

    for f in fields(class_or_instance=MapClass):
        with pytest.raises(ValueError):        
            get_type_str(f.type)
