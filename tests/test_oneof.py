from dataclasses import dataclass, fields
from typing import Annotated

import pytest

from makeproto.builder.make_msg import get_oneof_details
from makeproto.prototypes import BaseMessage, OneOf, OneOfKey


def test_ok():
    @dataclass
    class Hello(BaseMessage):
        a: Annotated[OneOf[str], OneOfKey("choice")]
        b: Annotated[OneOf[bytes], 123, "helloworld", OneOfKey("choice")]
        c: OneOf[int] = OneOfKey("choice")
        d: OneOf[bool] = OneOfKey("choice")

    exp = [
        ("choice", "a", str),
        ("choice", "b", bytes),
        ("choice", "c", int),
        ("choice", "d", bool),
    ]
    for i, f in enumerate(fields(Hello)):
        oodetails = get_oneof_details(f)
        assert oodetails == exp[i]


def test_fail():
    @dataclass
    class Hello(BaseMessage):
        a: OneOf[bool]
        b: Annotated[str, OneOfKey("choice")]
        c: Annotated[OneOf[list[str]], OneOfKey("choice")]
        d: Annotated[OneOf[bytes], 123, "helloworld"]
        g: OneOf[list[int]] = OneOfKey("foobar")
        aa: OneOf[str] = 3

    for f in fields(Hello):
        with pytest.raises(TypeError):
            get_oneof_details(f)
