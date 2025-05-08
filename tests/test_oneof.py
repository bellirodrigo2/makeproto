import sys
from dataclasses import dataclass, fields
from typing import Annotated, Any, Optional, get_type_hints

import pytest

from makeproto.makemsg import get_oneof_details
from makeproto.mapclass import dataclass_field_factory
from makeproto.prototypes import BaseMessage, OneOf, OneOfKey


def test_ok():
    @dataclass
    class Hello(BaseMessage):
        a: Annotated[OneOf[str], OneOfKey("choice")]
        b: Annotated[OneOf[bytes], 123, "helloworld", OneOfKey("choice")]
        c: Annotated[OneOf[int], OneOfKey("choice")]
        d: Annotated[OneOf[bool], OneOfKey("choice")]

    hints = get_type_hints(
        Hello, globalns=vars(sys.modules[Hello.__module__]), include_extras=True
    )

    exp = [
        ("choice", "a", "string", None),
        ("choice", "b", "bytes",None),
        ("choice", "c", "int64",None),
        ("choice", "d", "bool",None),
    ]
    for i, f in enumerate(fields(Hello)):
        hint: Optional[type[Any]] = hints.get(f.name, None)
        ftype = dataclass_field_factory(f, hint)
        oodetails = get_oneof_details(ftype)
        assert oodetails == exp[i]


def test_fail_syntax():
    @dataclass
    class Hello(BaseMessage):
        a: OneOf[bool]
        b: Annotated[str, OneOfKey("choice")]
        c: Annotated[OneOf[list[str]], OneOfKey("choice")]
        d: Annotated[OneOf[bytes], 123, "helloworld"]
        g: Annotated[OneOf[list[int]], OneOfKey("foobar")]
        aa: OneOf[str] = 3

    hints = get_type_hints(
        Hello, globalns=vars(sys.modules[Hello.__module__]), include_extras=True
    )

    for f in fields(Hello):
        hint: Optional[type[Any]] = hints.get(f.name, None)
        ftype = dataclass_field_factory(f, hint)
        with pytest.raises(TypeError):
            get_oneof_details(ftype)


def test_fail_types():
    @dataclass
    class Hello(BaseMessage):
        a: Annotated[OneOf[list[bool]], OneOfKey("choice")]
        b: Annotated[OneOf[dict[str, bool]], OneOfKey("choice")]

    hints = get_type_hints(
        Hello, globalns=vars(sys.modules[Hello.__module__]), include_extras=True
    )
    for f in fields(Hello):
        hint: Optional[type[Any]] = hints.get(f.name, None)
        ftype = dataclass_field_factory(f, hint)
        with pytest.raises(TypeError):
            get_oneof_details(ftype)
