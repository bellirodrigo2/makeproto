from typing import Optional

import pytest

from makeproto.prototypes import ProtoOption
from makeproto.tempmodels import Block, Field, Method


# Helpers
def make_field(name: str, ftype: Optional[type] = str, number: int = 1) -> Field:
    return Field(
        name=name, number=number, ftype=ftype, comment="", options=ProtoOption()
    )


def make_method(name: str) -> Method:
    class Dummy:
        pass

    return Method(
        method_name=name,
        request_type=Dummy,
        response_type=Dummy,
        request_stream=False,
        response_stream=False,
        comment="",
        options=ProtoOption(),
    )


# --- SERVICE BLOCK TESTS ---
def test_valid_service_block():
    block = Block(
        protofile="x.proto",
        package="pkg",
        name="S",
        block_type="service",
        fields={make_method("M")},
        reserved=[],
        comment="",
        options=ProtoOption(),
    )
    assert block.block_type == "service"


def test_invalid_service_block_with_field():
    with pytest.raises(TypeError):
        Block(
            protofile="x.proto",
            package="pkg",
            name="S",
            block_type="service",
            fields={make_field("f")},
            reserved=[],
            comment="",
            options=ProtoOption(),
        )


# --- ENUM BLOCK TESTS ---
def test_valid_enum_block():
    field = make_field("ENUM_VALUE", ftype=None)
    block = Block(
        protofile="x.proto",
        package="pkg",
        name="E",
        block_type="enum",
        fields={field},
        reserved=[],
        comment="",
        options=ProtoOption(),
    )
    assert block.block_type == "enum"


def test_enum_block_with_type_should_fail():
    field = make_field("ENUM_VALUE", ftype=int)
    with pytest.raises(TypeError):
        Block(
            protofile="x.proto",
            package="pkg",
            name="E",
            block_type="enum",
            fields={field},
            reserved=[],
            comment="",
            options=ProtoOption(),
        )


# --- MESSAGE BLOCK TESTS ---
def test_valid_message_block():
    block = Block(
        protofile="x.proto",
        package="pkg",
        name="M",
        block_type="message",
        fields={make_field("field", ftype=str)},
        reserved=[],
        comment="",
        options=ProtoOption(),
    )
    assert block.block_type == "message"


def test_message_block_with_missing_type_should_fail():
    field = make_field("field", ftype=None)
    with pytest.raises(TypeError):
        Block(
            protofile="x.proto",
            package="pkg",
            name="M",
            block_type="message",
            fields={field},
            reserved=[],
            comment="",
            options=ProtoOption(),
        )


def test_message_block_with_method_should_fail():
    with pytest.raises(TypeError):
        Block(
            protofile="x.proto",
            package="pkg",
            name="M",
            block_type="message",
            fields={make_method("m")},
            reserved=[],
            comment="",
            options=ProtoOption(),
        )


# --- ONEOF BLOCK TESTS ---
def test_valid_oneof_block():
    field = make_field("f", ftype=int)
    block = Block(
        protofile="x.proto",
        package="pkg",
        name="O",
        block_type="oneof",
        fields={field},
        reserved=[],
        comment="",
        options=ProtoOption(),
    )
    assert block.block_type == "oneof"


def test_oneof_block_with_no_type_should_fail():
    field = make_field("f", ftype=None)
    with pytest.raises(TypeError):
        Block(
            protofile="x.proto",
            package="pkg",
            name="O",
            block_type="oneof",
            fields={field},
            reserved=[],
            comment="",
            options=ProtoOption(),
        )


def test_oneof_block_with_method_should_fail():
    with pytest.raises(TypeError):
        Block(
            protofile="x.proto",
            package="pkg",
            name="O",
            block_type="oneof",
            fields={make_method("m")},
            reserved=[],
            comment="",
            options=ProtoOption(),
        )
