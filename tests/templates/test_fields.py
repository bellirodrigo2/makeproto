import pytest

from makeproto.templates import Field, Method, render_obj

# Testes para Field, Field de Enum e Method


@pytest.fixture
def field():
    """Retorna um objeto Field para testes"""
    return Field.make(name="field_name", number=1, type_="string", options={})


@pytest.fixture
def field_with_options():
    """Retorna um Field com opções"""
    return Field.make(
        name="field_name", number=1, type_="string", options={"opt1": "value1"}
    )


@pytest.fixture
def field_with_comment():
    """Retorna um Field com comentário"""
    return Field.make(
        name="field_name",
        number=1,
        type_="string",
        options={},
        comment="This is a field",
    )


@pytest.fixture
def field_with_options_and_comment():
    """Retorna um Field com opções e comentário"""
    return Field.make(
        name="field_name",
        number=1,
        type_="string",
        options={"opt1": "value1"},
        comment="This is a field",
    )


@pytest.fixture
def enum_field():
    """Retorna um Field de tipo enum"""
    return Field.make(name="enum_field", number=1)


@pytest.fixture
def enum_field_with_options():
    """Retorna um Field de tipo enum com opções"""
    return Field.make(name="enum_field", number=1, options={"opt1": "value1"})


@pytest.fixture
def method():
    """Retorna um objeto Method para testes"""
    return Method.make(
        method_name="myMethod",
        request_type="MyRequest",
        response_type="MyResponse",
        request_stream=False,
        response_stream=False,
    )


@pytest.fixture
def method_with_options():
    """Retorna um Method com opções"""
    return Method.make(
        method_name="myMethod",
        request_type="MyRequest",
        response_type="MyResponse",
        request_stream=False,
        response_stream=False,
        options={"opt1": "value1"},
    )


@pytest.fixture
def method_with_comment():
    """Retorna um Method com comentário"""
    return Method.make(
        method_name="myMethod",
        request_type="MyRequest",
        response_type="MyResponse",
        request_stream=False,
        response_stream=False,
        comment="This is a method",
    )


@pytest.fixture
def method_with_options_and_comment():
    """Retorna um Method com opções e comentário"""
    return Method.make(
        method_name="myMethod",
        request_type="MyRequest",
        response_type="MyResponse",
        request_stream=False,
        response_stream=False,
        options={"opt1": "value1"},
        comment="This is a method",
    )


def test_field_without_options_or_comment(field):
    """Testa o campo simples (Field) sem opções e sem comentário"""
    rendered = render_obj(field)
    expected = "string field_name = 1;"
    assert expected in rendered


def test_field_with_options(field_with_options):
    """Testa o campo simples (Field) com opções, sem comentário"""
    rendered = render_obj(field_with_options)
    expected = 'string field_name = 1 [opt1 = "value1"];'
    assert expected in rendered


def test_field_with_comment(field_with_comment):
    """Testa o campo simples (Field) com comentário"""
    rendered = render_obj(field_with_comment)
    assert "// This is a field" in rendered
    assert "string field_name = 1;" in rendered


def test_field_with_options_and_comment(field_with_options_and_comment):
    """Testa o campo simples (Field) com opções e comentário"""
    rendered = render_obj(field_with_options_and_comment)
    assert "// This is a field" in rendered
    assert 'string field_name = 1 [opt1 = "value1"]' in rendered


def test_enum_field_without_options(enum_field):
    """Testa o campo de Enum (Field) sem opções e sem comentário"""
    rendered = render_obj(enum_field)
    expected = "enum_field = 1;"
    assert expected in rendered


def test_enum_field_with_options(enum_field_with_options):
    """Testa o campo de Enum (Field) com opções"""
    rendered = render_obj(enum_field_with_options)
    expected = 'enum_field = 1 [opt1 = "value1"];'
    assert expected in rendered


def test_method_without_options_or_comment(method):
    """Testa o método sem opções e sem comentário"""
    rendered = render_obj(method)
    assert "rpc myMethod(MyRequest) returns (MyResponse) {" in rendered
    assert "option" not in rendered


def test_method_with_options(method_with_options):
    """Testa o método com opções"""
    rendered = render_obj(method_with_options)
    assert "rpc myMethod(MyRequest) returns (MyResponse) {" in rendered
    assert 'option opt1 = "value1";' in rendered


def test_method_with_comment(method_with_comment):
    """Testa o método com comentário"""
    rendered = render_obj(method_with_comment)
    assert "// This is a method" in rendered
    assert "rpc myMethod(MyRequest) returns (MyResponse) {" in rendered


def test_method_with_options_and_comment(method_with_options_and_comment):
    """Testa o método com opções e comentário"""
    rendered = render_obj(method_with_options_and_comment)
    assert "// This is a method" in rendered
    assert "rpc myMethod(MyRequest) returns (MyResponse) {" in rendered
    assert 'option opt1 = "value1";' in rendered


# Rodando os testes
if __name__ == "__main__":
    pytest.main()
