from dataclasses import dataclass
from typing import Annotated

import pytest

from makeproto.message import Message, inject_fields
from makeproto.prototypes import BaseMessage, Bool, Int32, OneOf, OneOfKey


@dataclass
class Message1(Message):
    a: Annotated[OneOf[str], OneOfKey("choice")]
    b: Annotated[OneOf[bytes], 123, "helloworld", OneOfKey("choice")]
    c: Annotated[OneOf[int], OneOfKey("choice")]
    d: Annotated[OneOf[Int32], OneOfKey("outro")]
    e: Annotated[OneOf[Bool], [], OneOfKey("outro")]


@dataclass
class Message2(Message): ...


@dataclass
class Message3(Message2):
    a: Annotated[OneOf[str], OneOfKey("choice")]
    b: Annotated[OneOf[bytes], 123, "helloworld", OneOfKey("choice")]
    c: Annotated[OneOf[int], OneOfKey("choice")]
    d: Annotated[OneOf[Int32], OneOfKey("outro")]
    e: Annotated[OneOf[Bool], [], OneOfKey("outro")]


inject_fields(Message1)
inject_fields(Message3)


@pytest.mark.parametrize("MSG", [Message1, Message3])
def test_msg(MSG: BaseMessage):

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


def test_multiple_set_same_oneof_should_fail():
    msg = Message1(a="hello", b=b"world", c=None, d=None, e=None)
    # Apenas o último campo definido deve permanecer
    assert msg.a is None
    assert msg.b is not None
    assert msg.WhichOneof("choice") == "b"


def test_switching_oneof_field_runtime():
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
    a: Annotated[OneOf[str], OneOfKey("x")]
    x: int = 0


inject_fields(MessageWithExtra)


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
    x: Annotated[OneOf[int], OneOfKey("mix")]


@dataclass
class ComplexMessage(BaseMessageWithExtra):
    y: Annotated[OneOf[str], OneOfKey("mix")]


inject_fields(ComplexMessage)


def test_multiple_inheritance_oneof():
    msg = ComplexMessage(x=None, y="go")
    assert msg.x is None
    assert msg.y == "go"
    assert msg.WhichOneof("mix") == "y"


def test_dynamic_attribute_setting():
    msg = Message1(a="start", b=None, c=None, d=None, e=None)
    setattr(msg, "b", b"bytes")
    assert msg.a is None
    assert msg.b is not None
    assert msg.WhichOneof("choice") == "b"
