from dataclasses import dataclass
from typing import Annotated

import pytest

from makeproto.message import Message, define_oneof_fields
from makeproto.prototypes2 import BaseMessage, Bool, Int32, OneOf


@dataclass
class Message1(Message):
    a: Annotated[str, OneOf("choice")]
    b: Annotated[bytes, 123, "helloworld", OneOf("choice")]
    c: Annotated[int, OneOf("choice")]
    d: Annotated[Int32, OneOf("outro")]
    e: Annotated[Bool, [], OneOf("outro")]


@dataclass
class Message2(Message): ...


@dataclass
class Message3(Message2):
    a: Annotated[str, OneOf("choice")]
    b: Annotated[bytes, 123, "helloworld", OneOf("choice")]
    c: Annotated[int, OneOf("choice")]
    d: Annotated[Int32, OneOf("outro")]
    e: Annotated[Bool, [], OneOf("outro")]


define_oneof_fields(Message1)
define_oneof_fields(Message3)


@pytest.mark.parametrize("MSG", [Message1, Message3])
def test_msg(MSG: BaseMessage) -> None:

    msg = MSG(a=None, b=b"foobar", c=None, d=32, e=None)

    assert msg.a is None
    assert msg.b is not None
    assert msg.c is None
    assert msg.d is not None
    assert msg.e is None
    assert msg.WhichOneof("choice") == "b"
    assert msg.WhichOneof("outro") == "d"

    msg.a = "hello"
    assert msg.a is not None
    assert msg.b is None
    assert msg.c is None
    assert msg.WhichOneof("choice") == "a"
    msg.e = True
    assert msg.d is None
    assert msg.e is not None
    assert msg.WhichOneof("outro") == "e"


def test_multiple_set_same_oneof_should_fail() -> None:
    msg = Message1(a="hello", b=b"world", c=None, d=None, e=None)
    # Apenas o último campo definido deve permanecer
    assert msg.a is None
    assert msg.b is not None
    assert msg.WhichOneof("choice") == "b"


def test_switching_oneof_field_runtime() -> None:
    msg = Message1(a="init", b=None, c=None, d=None, e=None)

    assert msg.WhichOneof("choice") == "a"
    msg.b = b"bytes"
    assert msg.a is None
    assert msg.b is not None
    assert msg.WhichOneof("choice") == "b"

    msg.c = 123
    assert msg.b is None
    assert msg.WhichOneof("choice") == "c"


@dataclass
class MessageWithExtra(Message):
    a: Annotated[str, OneOf("x")]
    x: int = 0


define_oneof_fields(MessageWithExtra)


def test_field_not_in_oneof_doesnt_affect_selected():
    msg = MessageWithExtra(a="hi", x=42)
    assert msg.WhichOneof("x") == "a"
    msg.x = 99
    assert msg.WhichOneof("x") == "a"  # still the same


def test_reassignment_same_field():
    msg = Message1(a="abc", b=None, c=None, d=None, e=None)
    msg.a = "xyz"  # reassign same field
    assert msg.a == "xyz"
    assert msg.WhichOneof("choice") == "a"


def test_no_oneof_set():
    msg = Message1(a=None, b=None, c=None, d=None, e=None)
    assert msg.WhichOneof("choice") is None
    assert msg.WhichOneof("outro") is None


@dataclass
class BaseMessageWithExtra(Message):
    x: Annotated[int, OneOf("mix")]


@dataclass
class ComplexMessage(BaseMessageWithExtra):
    y: Annotated[str, OneOf("mix")]


define_oneof_fields(ComplexMessage)


def test_multiple_inheritance_oneof() -> None:
    msg = ComplexMessage(x=None, y="go")
    assert msg.x is None
    assert msg.y == "go"
    assert msg.WhichOneof("mix") == "y"


def test_dynamic_attribute_setting() -> None:
    msg = Message1(a="start", b=None, c=None, d=None, e=None)
    setattr(msg, "b", b"bytes")
    assert msg.a is None
    assert msg.b is not None
    assert msg.WhichOneof("choice") == "b"
