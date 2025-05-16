import pytest

from makeproto.protoobj.types import Int32, String
from makeproto.template_models import Block, Field, Method
from makeproto.template_render import render_block, render_obj

# -------- Fixtures para fields e methods --------


class GetRequest: ...


class GetResponse: ...


@pytest.fixture
def simple_field() -> Field:
    return Field(name="id", number=1, ftype=Int32, options={}, comment="")


@pytest.fixture
def simple_enum() -> Field:
    return Field(name="id", number=1, ftype=None, options={}, comment="")


@pytest.fixture
def field_with_options() -> Field:
    return Field(
        name="id", number=1, ftype=Int32, options={"deprecated": True}, comment=""
    )


@pytest.fixture
def enum_with_options() -> Field:
    return Field(
        name="id", number=1, ftype=None, options={"deprecated": True}, comment=""
    )


@pytest.fixture
def simple_method() -> Method:

    return Method(
        method_name="GetItem",
        request_type=GetRequest,
        response_type=GetResponse,
        request_stream=False,
        response_stream=False,
        options={},
        comment="",
    )


@pytest.fixture
def method_with_options() -> Method:
    return Method(
        method_name="GetItem",
        request_type=GetRequest,
        response_type=GetResponse,
        request_stream=False,
        response_stream=False,
        options={"opt1": "value1"},
        comment="",
    )


# -------- Testes para Block --------


@pytest.mark.parametrize(
    "block_type,field_fixture",
    [
        ("message", "simple_field"),
        ("enum", "simple_enum"),
        ("oneof", "simple_field"),
        ("service", "simple_method"),
    ],
)
def test_block_without_options_or_comment(block_type, request, field_fixture):
    field = request.getfixturevalue(field_fixture)
    block = Block(
        protofile="proto",
        package="pack",
        name=f"My{block_type.title()}",
        block_type=block_type,
        fields=[field],
        comment="",
        options={},
        reserved=[],
    )
    rendered_fields = [render_obj(f) for f in block.fields]
    for r in rendered_fields:
        name = field.method_name if block_type == "service" else field.name
        assert name in r


@pytest.mark.parametrize(
    "block_type,field_fixture",
    [
        ("message", "field_with_options"),
        ("enum", "enum_with_options"),
        ("oneof", "field_with_options"),
    ],
)
def test_block_with_field_options(block_type, request, field_fixture):
    field = request.getfixturevalue(field_fixture)
    block = Block(
        protofile="proto",
        package="pack",
        name=f"My{block_type.title()}",
        block_type=block_type,
        fields=[field],
        comment="",
        options={},
        reserved=[],
    )
    rendered = [render_obj(f) for f in block.fields][0]
    assert "[deprecated = true]" in rendered


@pytest.mark.parametrize(
    "block_type,method_fixture",
    [
        ("service", "method_with_options"),
    ],
)
def test_service_block_with_method_options(block_type, request, method_fixture):
    method = request.getfixturevalue(method_fixture)
    block = Block(
        protofile="proto",
        package="pack",
        name="MyService",
        block_type=block_type,
        fields=[method],
        options={},
        comment="",
        reserved=[],
    )
    rendered = [render_obj(m) for m in block.fields][0]
    assert 'option opt1 = "value1";' in rendered


def test_block_with_comment_and_options(simple_field):
    block = Block(
        protofile="proto1",
        package="pack1",
        name="User",
        block_type="message",
        fields=[simple_field],
        comment="This is a message block",
        options={"opt_block": "true"},
        reserved=[],
    )
    assert block.comment == "This is a message block"
    assert block.options["opt_block"] == "true"


def test_message_block_with_oneof(simple_field: Field) -> None:
    oneof = Block(
        protofile="proto1",
        package="pack1",
        name="my_union",
        block_type="oneof",
        fields=[simple_field],
        comment="oneof comment",
        reserved=[],
        options={},
    )

    msg_block = Block(
        protofile="proto1",
        package="pack1",
        name="Container",
        block_type="message",
        fields=[oneof],
        comment="Message with oneof",
        reserved=[],
        options={},
    )

    rendered = render_block(msg_block)

    # Verifica se o oneof foi renderizado dentro do message
    assert "oneof my_union" in rendered
    assert "int32 id = 1;" in rendered
    assert "message Container" in rendered


def test_message_block_with_fields_and_oneof_with_options_and_comments():
    # Field direto no bloco message
    direct_field = Field(
        name="username",
        number=1,
        ftype=str,
        comment="User's name",
        options={"deprecated": True},
    )

    # Campos dentro do oneof
    oneof_field1 = Field(
        name="email",
        number=2,
        ftype=str,
        comment="User email",
        options={"required": True},
    )
    oneof_field2 = Field(
        name="phone",
        number=3,
        ftype=String,
        comment="User phone",
        options={"deprecated": False},
    )

    # Block com comentário e opções
    oneof = Block(
        protofile="proto1",
        package="pack1",
        name="contact",
        block_type="oneof",
        fields=[oneof_field1, oneof_field2],
        comment="Contact info, mutually exclusive",
        options={"opt_oneof": "yes"},
        reserved=[],
    )

    # Block contendo o field normal e o oneof
    message = Block(
        protofile="proto1",
        package="pack1",
        name="UserProfile",
        block_type="message",
        fields=[direct_field, oneof],
        comment="Profile of the user",
        options={"opt_msg": "true"},
        reserved=[],
    )

    rendered = render_block(message)

    # Asserts gerais
    assert "message UserProfile" in rendered
    assert "// Profile of the user" in rendered
    assert 'option opt_msg = "true";' in rendered

    # Field direto
    assert "// User's name" in rendered
    assert "string username = 1" in rendered
    assert "[deprecated = true]" in rendered

    # # Oneof e seus fields
    assert "oneof contact" in rendered
    assert "// Contact info, mutually exclusive" in rendered
    assert 'option opt_oneof = "yes";' in rendered
    assert "// User email" in rendered
    assert "string email = 2" in rendered
    assert "[required = true]" in rendered
    assert "// User phone" in rendered
    assert "string phone = 3" in rendered
    assert "[deprecated = false]" in rendered
