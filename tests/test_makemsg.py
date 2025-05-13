from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from typing_extensions import Annotated

from makeproto.exceptions import ProtoBlockError
from makeproto.makeblock import make_msgblock
from makeproto.models import Block
from makeproto.prototypes import (
    BaseMessage,
    Bool,
    Bytes,
    FieldSpec,
    Fixed64,
    Int32,
    OneOf,
    String,
    UInt32,
)


class Proto1(BaseMessage):
    protofile = "proto"
    package = "pack1"


class MyEnum(Proto1, Enum):
    VALID = 0
    INVALID = 1


class Enum2(Proto1, Enum):
    FOO = 0
    BAR = 1


@dataclass
class Hello(Proto1):

    comment = "Hello Comment"
    options = {"foo": "bar"}

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

    block = make_msgblock(Hello)
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

    comment = 8
    options = [1, 2, 3]

    a: Annotated[str, OneOf(key=3)]
    b: Annotated[Path, 123]
    c: Annotated[String, FieldSpec(index=-1)]
    d: Annotated[bytes, 123, "helloworld", OneOf(key="choice", index="4")]
    e: Optional[str]
    f: Dict[bytes, str]
    g: List[Path]
    h: Dict[int, Union[str, int]]
    i: int = FieldSpec(comment=[])
    j: str = FieldSpec(options={3: "bar"})
    k: str = FieldSpec(options={"3": 3})
    lee: str = FieldSpec(options=[1])


def test_get_dataclass_block_fail() -> None:

    try:
        make_msgblock(Fail)
    except ProtoBlockError as e:
        assert len(e) == 14


class Hello2(Proto1):

    comment = "ClassicClass"

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

    block = make_msgblock(Hello2)
    assert len(block.fields) == 13
    assert len([x for x in block.fields if isinstance(x, Block)]) == 2
    assert block.name == "Hello2"
    assert block.comment == "ClassicClass"

    for field in block.fields:
        if isinstance(field, Block):
            assert field.block_type == "oneof"
