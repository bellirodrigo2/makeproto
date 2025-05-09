import pytest

from makeproto.models import (
    EnumBlock,
    Field,
    MessageBlock,
    Method,
    OneOfBlock,
    ServiceBlock,
)
from makeproto.templates import render_block, render_obj

# -------- Fixtures para fields e methods --------


class GetRequest:...
class GetResponse:...

@pytest.fixture
def simple_field():
    return Field.make(name="id", number=1, type_="int32")


@pytest.fixture
def field_with_options():
    return Field.make(name="id", number=1, type_="int32", options={"deprecated": True})


@pytest.fixture
def simple_method():

    return Method.make(
        method_name="GetItem",
        request_type=GetRequest,
        response_type=GetResponse,
        request_stream=False,
        response_stream=False,
    )


@pytest.fixture
def method_with_options():
    return Method.make(
        method_name="GetItem",
        request_type=GetRequest,
        response_type=GetResponse,
        request_stream=False,
        response_stream=False,
        options={"opt1": "value1"},
    )


# -------- Testes para Block --------


@pytest.mark.parametrize(
    "block_type,block_class,field_fixture",
    [
        ("message", MessageBlock, "simple_field"),
        ("enum", EnumBlock, "simple_field"),
        ("oneof", OneOfBlock, "simple_field"),
        ("service", ServiceBlock, "simple_method"),
    ],
)
def test_block_without_options_or_comment(
    block_type, block_class, request, field_fixture
):
    field = request.getfixturevalue(field_fixture)
    block = block_class.make(
        name=f"My{block_type.title()}", block_type=block_type, fields=[field]
    )
    rendered_fields = [render_obj(f) for f in block.fields]
    for r in rendered_fields:
        name = field.method_name if block_type == "service" else field.name
        assert name in r


@pytest.mark.parametrize(
    "block_type,block_class,field_fixture",
    [
        ("message", MessageBlock, "field_with_options"),
        ("enum", EnumBlock, "field_with_options"),
        ("oneof", OneOfBlock, "field_with_options"),
    ],
)
def test_block_with_field_options(block_type, block_class, request, field_fixture):
    field = request.getfixturevalue(field_fixture)
    block = block_class.make(
        name=f"My{block_type.title()}", block_type=block_type, fields=[field]
    )
    rendered = [render_obj(f) for f in block.fields][0]
    assert "[deprecated = true]" in rendered


@pytest.mark.parametrize(
    "block_type,block_class,method_fixture",
    [
        ("service", ServiceBlock, "method_with_options"),
    ],
)
def test_service_block_with_method_options(
    block_type, block_class, request, method_fixture
):
    method = request.getfixturevalue(method_fixture)
    block = block_class.make(name="MyService", block_type=block_type, fields=[method])
    rendered = [render_obj(m) for m in block.fields][0]
    assert 'option opt1 = "value1";' in rendered


def test_block_with_comment_and_options(simple_field):
    block = MessageBlock.make(
        name="User",
        block_type="message",
        fields=[simple_field],
        comment="This is a message block",
        options={"opt_block": "true"},
    )
    assert block.comment == "This is a message block"
    assert block.options["opt_block"] == "true"


def test_message_block_with_oneof(simple_field):
    oneof = OneOfBlock.make(
        name="my_union",
        block_type="oneof",
        fields=[simple_field],
        comment="oneof comment",
    )

    msg_block = MessageBlock.make(
        name="Container",
        block_type="message",
        fields=[oneof],
        comment="Message with oneof",
    )

    rendered = render_block(msg_block)

    # Verifica se o oneof foi renderizado dentro do message
    assert "oneof my_union" in rendered
    assert "int32 id = 1;" in rendered
    assert "message Container" in rendered


def test_message_block_with_fields_and_oneof_with_options_and_comments():
    # Field direto no bloco message
    direct_field = Field.make(
        name="username",
        number=1,
        type_="string",
        comment="User's name",
        options={"deprecated": True},
    )

    # Campos dentro do oneof
    oneof_field1 = Field.make(
        name="email",
        number=2,
        type_="string",
        comment="User email",
        options={"required": True},
    )
    oneof_field2 = Field.make(
        name="phone",
        number=3,
        type_="string",
        comment="User phone",
        options={"deprecated": False},
    )

    # OneOfBlock com comentário e opções
    oneof = OneOfBlock.make(
        name="contact",
        block_type="oneof",
        fields=[oneof_field1, oneof_field2],
        comment="Contact info, mutually exclusive",
        options={"opt_oneof": "yes"},
    )

    # MessageBlock contendo o field normal e o oneof
    message = MessageBlock.make(
        name="UserProfile",
        block_type="message",
        fields=[direct_field, oneof],
        comment="Profile of the user",
        options={"opt_msg": "true"},
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

    # Oneof e seus fields
    assert "oneof contact" in rendered
    assert "// Contact info, mutually exclusive" in rendered
    assert 'option opt_oneof = "yes";' in rendered
    assert "// User email" in rendered
    assert "string email = 2" in rendered
    assert "[required = true]" in rendered
    assert "// User phone" in rendered
    assert "string phone = 3" in rendered
    assert "[deprecated = false]" in rendered
