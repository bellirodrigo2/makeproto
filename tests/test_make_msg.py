from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated, Counter

import pytest

from makeproto.builder.make_msg import get_templates, make_enum_proto_str, make_message_proto_str
from makeproto.builder.templates import OneOfTemplate
from makeproto.prototypes import (
    BaseMessage,
    Bool,
    Bytes,
    Enum,
    Fixed64,
    Int32,
    OneOf,
    OneOfKey,
    String,
    UInt32,
)


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
    y: OneOf[int] = OneOfKey("outro")
    z: OneOf[bool] = OneOfKey("outro")


def test_get_template_ok():

    templates = get_templates(Hello)
    assert len(templates) == 13
    assert len([x for x in templates if isinstance(x, OneOfTemplate)]) == 2


def test_get_template_fail():
    @dataclass
    class Fail(BaseMessage):
        aça:str

    with pytest.raises(ValueError):
        get_templates(Fail)


def test_msg_template():

    # MYENUM2 = make_enum_proto_str(MyEnum)
    # ENUM2 = make_enum_proto_str(Enum2)

    msg_str = make_message_proto_str(Hello)

    assert msg_str.startswith('message Hello {')
    # with open("teste.proto", "w", encoding="utf-8") as f:
        # f.write(f"""syntax = "proto3";\n{MYENUM2}\n{ENUM2}\n{msg_str}""")

def test_msg_template_fail():

    with pytest.raises(TypeError):

        @dataclass
        class MyS(BaseMessage):
            a: OneOf[str] = OneOfKey(3)
