import pytest
from makeproto.models import Field, Method, MessageBlock, EnumBlock, OneOfBlock, ServiceBlock
from makeproto.templates2 import render_obj
# -------- Fixtures para fields e methods --------

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
        request_type="GetRequest",
        response_type="GetResponse",
        request_stream=False,
        response_stream=False
    )

@pytest.fixture
def method_with_options():
    return Method.make(
        method_name="GetItem",
        request_type="GetRequest",
        response_type="GetResponse",
        request_stream=False,
        response_stream=False,
        options={"opt1": "value1"}
    )

# -------- Testes para Block --------

@pytest.mark.parametrize("block_type,block_class,field_fixture", [
    ("message", MessageBlock, "simple_field"),
    ("enum", EnumBlock, "simple_field"),
    ("oneof", OneOfBlock, "simple_field"),
    ("service", ServiceBlock, "simple_method"),
])
def test_block_without_options_or_comment(block_type, block_class, request, field_fixture):
    field = request.getfixturevalue(field_fixture)
    block = block_class.make(name=f"My{block_type.title()}", block_type=block_type, fields=[field])
    rendered_fields = [render_obj(f) for f in block.fields]
    for r in rendered_fields:
        name = field.method_name if block_type == 'service' else field.name
        assert name in r

@pytest.mark.parametrize("block_type,block_class,field_fixture", [
    ("message", MessageBlock, "field_with_options"),
    ("enum", EnumBlock, "field_with_options"),
    ("oneof", OneOfBlock, "field_with_options"),
])
def test_block_with_field_options(block_type, block_class, request, field_fixture):
    field = request.getfixturevalue(field_fixture)
    block = block_class.make(name=f"My{block_type.title()}", block_type=block_type, fields=[field])
    rendered = [render_obj(f) for f in block.fields][0]
    assert "[deprecated = true]" in rendered

@pytest.mark.parametrize("block_type,block_class,method_fixture", [
    ("service", ServiceBlock, "method_with_options"),
])
def test_service_block_with_method_options(block_type, block_class, request, method_fixture):
    method = request.getfixturevalue(method_fixture)
    block = block_class.make(name="MyService", block_type=block_type,fields=[method])
    rendered = [render_obj(m) for m in block.fields][0]
    assert 'option opt1 = "value1";' in rendered

def test_block_with_comment_and_options(simple_field):
    block = MessageBlock.make(
        name="User",
        block_type='message',
        fields=[simple_field],
        comment="This is a message block",
        options={"opt_block": "true"}
    )
    assert block.comment == "This is a message block"
    assert block.options["opt_block"] == "true"
