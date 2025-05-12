import pytest

from makeproto.templates import Field, Method, render_obj


class MyResponse: ...


class MyRequest: ...


@pytest.fixture
def field() -> Field:
    return Field(name="field_name", number=1, ftype=str, options={}, comment="")


@pytest.fixture
def field_with_options() -> Field:
    return Field(
        name="field_name", number=1, ftype=str, options={"opt1": "value1"}, comment=""
    )


@pytest.fixture
def field_with_comment() -> Field:
    return Field(
        name="field_name",
        number=1,
        ftype=str,
        options={},
        comment="This is a field",
    )


@pytest.fixture
def field_with_options_and_comment() -> Field:
    return Field(
        name="field_name",
        number=1,
        ftype=str,
        options={"opt1": "value1"},
        comment="This is a field",
    )


@pytest.fixture
def enum_field() -> Field:
    return Field(name="enum_field", number=1, ftype=None, options={}, comment="")


@pytest.fixture
def enum_field_with_options() -> Field:
    return Field(
        name="enum_field",
        number=1,
        options={"opt1": "value1"},
        ftype=None,
        comment="",
    )


@pytest.fixture
def method() -> Method:
    return Method(
        method_name="myMethod",
        request_type=MyRequest,
        response_type=MyResponse,
        request_stream=False,
        response_stream=False,
        options={},
        comment="",
    )


@pytest.fixture
def method_with_options() -> Method:
    return Method(
        method_name="myMethod",
        request_type=MyRequest,
        response_type=MyResponse,
        request_stream=False,
        response_stream=False,
        options={"opt1": "value1"},
        comment="",
    )


@pytest.fixture
def method_with_comment() -> Method:
    return Method(
        method_name="myMethod",
        request_type=MyRequest,
        response_type=MyResponse,
        request_stream=False,
        response_stream=False,
        comment="This is a method",
        options={},
    )


@pytest.fixture
def method_with_options_and_comment() -> Method:
    return Method(
        method_name="myMethod",
        request_type=MyRequest,
        response_type=MyResponse,
        request_stream=False,
        response_stream=False,
        options={"opt1": "value1"},
        comment="This is a method",
    )


def test_field_without_options_or_comment(field: Field) -> None:
    rendered = render_obj(field)
    expected = "string field_name = 1;"
    assert expected in rendered


def test_field_with_options(field_with_options) -> None:
    rendered = render_obj(field_with_options)
    expected = 'string field_name = 1 [opt1 = "value1"];'
    assert expected in rendered


def test_field_with_comment(field_with_comment) -> None:
    rendered = render_obj(field_with_comment)
    assert "// This is a field" in rendered
    assert "string field_name = 1;" in rendered


def test_field_with_options_and_comment(field_with_options_and_comment) -> None:
    rendered = render_obj(field_with_options_and_comment)
    assert "// This is a field" in rendered
    assert 'string field_name = 1 [opt1 = "value1"]' in rendered


def test_enum_field_without_options(enum_field: Field) -> None:
    """Testa o campo de Enum (Field) sem opções e sem comentário"""
    rendered = render_obj(enum_field)
    expected = "enum_field = 1;"
    assert expected in rendered


def test_enum_field_with_options(enum_field_with_options: Field) -> None:
    rendered = render_obj(enum_field_with_options)
    expected = 'enum_field = 1 [opt1 = "value1"];'
    assert expected in rendered


def test_method_without_options_or_comment(method: Method) -> None:
    rendered = render_obj(method)
    assert "rpc myMethod(MyRequest) returns (MyResponse) {" in rendered
    assert "option" not in rendered


def test_method_with_options(method_with_options: Method) -> None:
    rendered = render_obj(method_with_options)
    assert "rpc myMethod(MyRequest) returns (MyResponse) {" in rendered
    assert 'option opt1 = "value1";' in rendered


def test_method_with_comment(method_with_comment):
    rendered = render_obj(method_with_comment)
    assert "// This is a method" in rendered
    assert "rpc myMethod(MyRequest) returns (MyResponse) {" in rendered


def test_method_with_options_and_comment(method_with_options_and_comment):
    rendered = render_obj(method_with_options_and_comment)
    assert "// This is a method" in rendered
    assert "rpc myMethod(MyRequest) returns (MyResponse) {" in rendered
    assert 'option opt1 = "value1";' in rendered


# Rodando os testes
if __name__ == "__main__":
    pytest.main()
