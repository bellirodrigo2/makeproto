import pytest

from makeproto.templates import (
    EnumTemplate,
    KeyNumber,
    MessageTemplate,
    OneOfTemplate,
    StdFieldTemplate,
)


@pytest.mark.parametrize(
    "type, name, number, expected",
    [
        ("hello", "world", 0, "hello world = 0;"),
        ("foo", "bar", 1, "foo bar = 1;"),
        ("type", "name", 7, "type name = 7;"),
    ],
)
def test_std_field_ok(type, name, number, expected):

    template = StdFieldTemplate(type, name, number)

    field = template.build()
    assert expected in field


def test_std_field_ok_comments_json():

    template = StdFieldTemplate("string", "name", 7, "comments1", "jsonalias")

    field = template.build()
    assert field.startswith("// comments1")
    assert field.endswith('[json_name = "jsonalias"];')

    template = StdFieldTemplate("string", "name", 7, None, "jsonalias")

    field = template.build()
    assert field.startswith("string")
    assert field.endswith('[json_name = "jsonalias"];')

    template = StdFieldTemplate("string", "name", 7, "comments1")

    field = template.build()
    assert field.startswith("// comments1")
    assert field.endswith("7;")


@pytest.mark.parametrize(
    "type, name, number",
    [
        ("hello", "world", None),
        ("hello", None, 0),
        (None, "world", 0),
        ("hello", "world", []),
        ("hello", [], 0),
        ([], "world", 0),
    ],
)
def test_std_field_raise(type, name, number):

    with pytest.raises(TypeError):
        StdFieldTemplate(type, name, number)


# ----------- ENUM TESTS --------------


@pytest.mark.parametrize(
    "name,values, expected_snippet",
    [
        (
            "Color",
            [KeyNumber("RED", 0), KeyNumber("BLUE", 1)],
            "enum Color",
        ),
        (
            "Status",
            [KeyNumber("ON", 1), KeyNumber("OFF", 0)],
            "ON = 1",
        ),
    ],
)
def test_enum_ok(name, values, expected_snippet):
    template = EnumTemplate(name, values)
    result = template.build()
    assert expected_snippet in result


@pytest.mark.parametrize(
    "name, values",
    [
        (None, [KeyNumber("ON", 1)]),
        ("Color", "not-a-list"),
        (123, [KeyNumber("ON", 1)]),
    ],
)
def test_enum_raise(name, values):
    with pytest.raises(TypeError):
        EnumTemplate(name, values).build()


def test_enum_raise2():
    with pytest.raises(TypeError):
        KeyNumber("ON", "hello")
    with pytest.raises(TypeError):
        KeyNumber("ON", None)
    with pytest.raises(TypeError):
        KeyNumber("ON", [])
    with pytest.raises(TypeError):
        KeyNumber(1, 1)


# ----------- ONEOF TESTS --------------


@pytest.mark.parametrize(
    "name, fields, expected_snippet",
    [
        (
            "choice",
            [StdFieldTemplate("int32", "id", 1), StdFieldTemplate("string", "name", 2)],
            "oneof choice",
        ),
    ],
)
def test_oneof_ok(name, fields, expected_snippet):
    template = OneOfTemplate(name, fields)
    result = template.build()
    assert expected_snippet in result


@pytest.mark.parametrize(
    "name, fields",
    [
        ("choice", None),
        ("choice", "not-a-list"),
        ("choice", [("int32", "id", 1)]),
        (None, [StdFieldTemplate("int32", "id", 1)]),
    ],
)
def test_oneof_raise(name, fields):
    with pytest.raises(TypeError):
        OneOfTemplate(name, fields).build()


# ----------- MESSAGE TESTS --------------


@pytest.mark.parametrize(
    "name, fields, expected_snippet",
    [
        ("Person", ["int32 id = 1", "string name = 2"], "message Person"),
    ],
)
def test_message_ok(name, fields, expected_snippet):
    template = MessageTemplate(name, fields)
    result = template.build()
    assert expected_snippet in result


@pytest.mark.parametrize(
    "name, fields",
    [
        ("Person", None),
        (None, ["int32 id = 1"]),
        ("Person", 1),
        ("Person", [123, 456]),
    ],
)
def test_message_raise(name, fields):
    with pytest.raises(TypeError):
        MessageTemplate(name, fields).build()
