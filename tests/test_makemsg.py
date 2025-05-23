from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from typing_extensions import Annotated

from makeproto.exceptions import ProtoBlockError
from makeproto.makeblock import make_msgblock
from makeproto.protoobj.base import FieldSpec, OneOf, ProtoOption
from makeproto.protoobj.message import BaseMessage
from makeproto.protoobj.types import Bool, Bytes, Fixed64, Int32, String, UInt32
from makeproto.template_models import Block


class Proto1(BaseMessage):
    @classmethod
    def protofile(cls) -> str:
        return "proto"

    @classmethod
    def package(cls) -> str:
        return "pack1"


class MyEnum(Proto1, Enum):
    VALID = 0
    INVALID = 1


class Enum2(Proto1, Enum):
    FOO = 0
    BAR = 1


@dataclass
class Hello(Proto1):

    @classmethod
    def comment(cls) -> str:
        return "Hello Comment"

    @classmethod
    def options(cls) -> ProtoOption:
        return {"foo": "bar"}

    a: Annotated[str, OneOf(key="choice")]
    aa: Annotated[Int32, OneOf(key="choice")]
    bb: Annotated[String, OneOf(key="choice")]
    b: Annotated[bytes, 123, "helloworld", OneOf(key="choice")]
    c: String
    d: str
    e: UInt32
    f: Annotated[int, FieldSpec(options={"deprecated": True, "json_name": "f_alias"})]
    g: MyEnum
    h: Annotated[Enum2, "helloworld"]
    i: Annotated[Fixed64, 1234]
    j: list[str]
    k: Annotated[
        list[Bool], 1, FieldSpec(options={"deprecated": True, "json_name": "k_alias"})
    ]
    li: dict[str, MyEnum]
    m: dict[Int32, Bytes] = FieldSpec(comment='Comment for "m"')
    y: int = OneOf(key="outro")
    z: bool = OneOf(key="outro")


def test_get_dataclass_block_ok() -> None:

    block = make_msgblock(Hello, "", "")
    assert len(block.fields) == 13
    assert len([x for x in block.fields if isinstance(x, Block)]) == 2
    assert block.name == "Hello"
    assert block.comment == "Hello Comment"
    assert block.options["foo"] == "bar"

    for field in block.fields:
        if isinstance(field, Block):
            assert field.block_type == "oneof"


@dataclass
class Fail(Proto1):

    @classmethod
    def comment(cls) -> str:
        return 8

    @classmethod
    def options(cls) -> ProtoOption:
        return [1, 2, 3]

    a: Annotated[str, OneOf(key=3)]
    b: Annotated[Path, 123]
    c: Annotated[String, FieldSpec(index=-1)]
    d: Annotated[bytes, 123, "helloworld", OneOf(key="choice", index="4")]
    e: Optional[str]
    f: Dict[bytes, str]
    g: List[Path]
    h: Dict[int, Union[str, int]]
    i: int = FieldSpec(comment=[], index=45)
    j: str = FieldSpec(options={3: "bar"}, index=45)
    k: str = FieldSpec(options={"3": 3})
    lee: str = FieldSpec(options=[1])


def test_get_dataclass_block_fail() -> None:

    try:
        make_msgblock(Fail, "", "")
    except ProtoBlockError as e:
        assert len(e) == 16


class Hello2(Proto1):

    @classmethod
    def comment(cls) -> str:
        return "ClassicClass"

    def __init__(
        self,
        a: Annotated[str, OneOf(key="choice")],
        b: Annotated[Int32, OneOf(key="choice")],
        c: Annotated[String, OneOf(key="choice")],
        d: Annotated[bytes, 123, "helloworld", OneOf(key="choice")],
        e: String,
        f: str,
        g: UInt32,
        h: Annotated[
            int, FieldSpec(options={"deprecated": True, "json_name": "f_alias"})
        ],
        i: MyEnum,
        j: Annotated[Enum2, "helloworld"],
        k: Annotated[Fixed64, 1234],
        leee: list[str],
        m: Annotated[
            list[Bool],
            1,
            FieldSpec(options={"deprecated": True, "json_name": "k_alias"}),
        ],
        n: dict[str, MyEnum],
        o: Annotated[dict[Int32, Bytes], [], FieldSpec(comment='Comment for "m"')],
        p: Annotated[int, OneOf(key="outro")],
        q: Annotated[bool, OneOf(key="outro")],
    ) -> None: ...


def test_get_class_block_ok() -> None:

    block = make_msgblock(Hello2, "", "")
    assert len(block.fields) == 13
    assert len([x for x in block.fields if isinstance(x, Block)]) == 2
    assert block.name == "Hello2"
    assert block.comment == "ClassicClass"

    for field in block.fields:
        if isinstance(field, Block):
            assert field.block_type == "oneof"


@dataclass
class Base(Proto1):

    @classmethod
    def comment(cls) -> str:
        return "Base Comment"

    @classmethod
    def options(cls) -> ProtoOption:
        return {"base": "foo"}

    b1: Annotated[str, OneOf(key="choice")]
    b2: Annotated[Int32, OneOf(key="choice")]


@dataclass
class Derived1(Base):

    @classmethod
    def comment(cls) -> str:
        return "Derived1 Comment"

    @classmethod
    def options(cls) -> ProtoOption:
        return {"der1": "base"}

    fromder1: int


@dataclass
class Derived2(Derived1):

    @classmethod
    def comment(cls) -> str:
        return "Derived2 Comment"

    @classmethod
    def options(cls) -> ProtoOption:
        return {}

    fromder2: bool


def test_nested() -> None:
    base_block = make_msgblock(Base, "", "")

    assert base_block.comment == "Base Comment"
    assert base_block.options["base"] == "foo"
    assert len(base_block.fields) == 1
    block_oo = next(iter((base_block.fields)))
    assert block_oo.name == "choice"
    assert isinstance(block_oo, Block)
    assert len(block_oo) == 2

    der1_block = make_msgblock(Derived1, "", "")
    assert der1_block.comment == "Derived1 Comment"
    assert der1_block.options["der1"] == "base"
    assert len(der1_block.fields) == 2

    der2_block = make_msgblock(Derived2, "", "")
    assert der2_block.comment == "Derived2 Comment"
    assert der2_block.options == {}
    assert len(der2_block.fields) == 3
