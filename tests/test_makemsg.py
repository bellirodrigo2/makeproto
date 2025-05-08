
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated

import pytest

from makeproto.makemsg import make_msgblock
from makeproto.models import Block
from makeproto.prototypes import BaseMessage, Bool, Bytes, FieldSpec, Fixed64, Int32, OneOf, OneOfKey, String, UInt32


class MyEnum(Enum):
    VALID = 0
    INVALID = 1


class Enum2(Enum):
    FOO = 0
    BAR = 1


@dataclass
class Hello(BaseMessage):
    ga: type
    nou: tuple[str, ...]
    a: Annotated[OneOf[str], OneOfKey("choice")]
    aa: Annotated[OneOf[Int32], OneOfKey("choice")]
    bb: Annotated[OneOf[String], OneOfKey("choice")]
    b: Annotated[OneOf[bytes], 123, "helloworld", OneOfKey("choice")]
    c: String
    d: str
    e: UInt32
    f: Annotated[int, "foobar", FieldSpec(options={'deprecated':True, 'json_name':'f_alias'})]
    g: MyEnum
    h: Annotated[Enum2, "helloworld"]
    i: Annotated[Fixed64, 1234]
    j: list[str]
    k: Annotated[list[Bool], 1,FieldSpec(options={'deprecated':True, 'json_name':'k_alias'})]
    l: dict[str, MyEnum]
    m: Annotated[dict[Int32, Bytes], [], FieldSpec(comment='Comment for "m"')]
    n: datetime
    o: Path
    p: Counter[int]
    y: Annotated[OneOf[int], OneOfKey("outro")]
    z: Annotated[OneOf[bool], OneOfKey("outro")]

    spec:FieldSpec = FieldSpec(comment='Hello Comment', options={'foo':'bar'})


def test_get_template_ok():

    block = make_msgblock(Hello)
    assert len(block.fields) == 13
    assert len([x for x in block.fields if isinstance(x, Block)]) == 2
    assert block.name == 'Hello'
    assert block.comment == 'Hello Comment'
    assert block.options['foo'] == 'bar'


def test_get_template_error():

    with pytest.raises(ValueError, match="Invalid Field"):
        make_msgblock(Hello, ignore_error=False)


def test_get_template_fail():
    @dataclass
    class Fail(BaseMessage):
        aça: str

    with pytest.raises(ValueError, match="proto identifier"):
        make_msgblock(Fail)


def test_get_template_fail2():
    @dataclass
    class Fail(BaseMessage):
        aca: str = "hello"

    with pytest.raises(ValueError, match="Data Field cannot "):
        make_msgblock(Fail)
