from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated, Counter

import pytest

from makeproto.makemsg import get_templates, make_message_proto_str
from makeproto.prototypes import (
    BaseMessage,
    Bool,
    Bytes,
    Fixed64,
    Int32,
    OneOf,
    OneOfKey,
    String,
    UInt32,
)
from makeproto.templates import OneOfTemplate
from enum import Enum


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
    f: Annotated[int, "foobar"]
    g: MyEnum
    h: Annotated[Enum2, "helloworld"]
    i: Annotated[Fixed64, 1234]
    j: list[str]
    k: Annotated[list[Bool], 1]
    l: dict[str, MyEnum]
    m: Annotated[dict[Int32, Bytes], []]
    n: datetime
    o: Path
    p: Counter[int]
    y: Annotated[OneOf[int], OneOfKey("outro")]
    z: Annotated[OneOf[bool], OneOfKey("outro")]


def test_get_template_ok():

    templates = get_templates(Hello)
    assert len(templates) == 13
    assert len([x for x in templates if isinstance(x, OneOfTemplate)]) == 2


def test_get_template_error():

    with pytest.raises(ValueError, match="Invalid Field"):
        get_templates(Hello, ignore_error=False)


def test_get_template_fail():
    @dataclass
    class Fail(BaseMessage):
        aça: str

    with pytest.raises(ValueError, match="proto identifier"):
        get_templates(Fail)


def test_get_template_fail2():
    @dataclass
    class Fail(BaseMessage):
        aca: str = "hello"

    with pytest.raises(ValueError, match="Data Field cannot "):
        get_templates(Fail)


def test_msg_template():

    msg_str = make_message_proto_str(Hello)

    assert msg_str.startswith("message Hello {")
    assert "string" in msg_str
    assert "repeated bool" in msg_str
    assert "map<string, MyEnum>" in msg_str
    assert "map<int32, bytes>" in msg_str
    assert msg_str.endswith("}")
