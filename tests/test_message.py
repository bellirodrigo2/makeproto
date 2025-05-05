from dataclasses import dataclass
from typing import Annotated

from makeproto.message import Message
from makeproto.prototypes import Bool, Int32, OneOf, OneOfKey


@dataclass
class Message1(Message):
    a: Annotated[OneOf[str], OneOfKey("choice")]
    b: Annotated[OneOf[bytes], 123, "helloworld", OneOfKey("choice")]
    c: Annotated[OneOf[int], OneOfKey("choice")]
    d: Annotated[OneOf[Int32], OneOfKey("outro")]
    e: Annotated[OneOf[Bool], [], OneOfKey("outro")]


def test_msg():

    msg = Message1(a=None, b=b"foobar", c=None, d=32, e=None)

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
