import pytest

from makeproto.compiler import CompilerContext
from makeproto.setters.name import (
    NameSetter,
    NameTransformStrategy,
    normalize_name,
    to_camel_case,
    to_pascal_case,
    to_snake_case,
)
from makeproto.template import MethodTemplate, ServiceTemplate
from tests.test_helpers import make_method, make_service

# ---------- Funções auxiliares ----------


def test_to_snake_case() -> None:
    assert to_snake_case("SomeName") == "some_name"
    assert to_snake_case("someName") == "some_name"
    assert to_snake_case("Some Name-With--Dashes") == "some_name_with_dashes"
    assert to_snake_case("already_snake_case") == "already_snake_case"


def test_to_camel_case() -> None:
    assert to_camel_case("some_name") == "someName"
    assert to_camel_case("Some_Name") == "someName"
    assert to_camel_case("some-name-with-dashes") == "someNameWithDashes"
    assert to_camel_case("alreadyCamelCase") == "alreadyCamelCase"


def test_to_pascal_case() -> None:
    assert to_pascal_case("some_name") == "SomeName"
    assert to_pascal_case("some-name-with-dashes") == "SomeNameWithDashes"
    assert to_pascal_case("AlreadyPascalCase") == "Alreadypascalcase"


def test_normalize_name() -> None:
    assert normalize_name("someName", NameTransformStrategy.SNAKE_CASE) == "some_name"
    assert normalize_name("some_name", NameTransformStrategy.CAMEL_CASE) == "someName"
    assert normalize_name("some_name", NameTransformStrategy.PASCAL_CASE) == "SomeName"
    assert (
        normalize_name("some_name", NameTransformStrategy.NO_TRANSFORM) == "some_name"
    )


# ---------- Fixtures ----------


@pytest.fixture
def context() -> CompilerContext:
    return CompilerContext()


@pytest.fixture
def block() -> ServiceTemplate:
    return make_service("ValidBlock")


# ---------- Testes NameSetter ----------


def test_visit_field_and_method_no_transform(
    block: ServiceTemplate, context: CompilerContext
) -> None:
    field: MethodTemplate = make_method("FieldName", service=block)
    method: MethodTemplate = make_method("MethodName", service=block)
    normalizer = NameSetter()
    normalizer.execute([block], context)
    assert block.name == "ValidBlock"
    assert field.name == "FieldName"
    assert method.name == "MethodName"


def test_visit_field_and_method_snake(
    block: ServiceTemplate, context: CompilerContext
) -> None:
    field: MethodTemplate = make_method("FieldName", service=block)
    method: MethodTemplate = make_method("MethodName", service=block)
    normalizer = NameSetter("snake_case")
    normalizer.execute([block], context)
    assert block.name == "valid_block"
    assert field.name == "field_name"
    assert method.name == "method_name"


def test_camel_case(context: CompilerContext) -> None:
    block: ServiceTemplate = make_service("block_name")
    field1: MethodTemplate = make_method("field_one", service=block)
    field2: MethodTemplate = make_method("field_two", service=block)
    normalizer = NameSetter("camel_case")
    normalizer.execute([block], context)
    assert block.name == "blockName"
    assert field1.name == "fieldOne"
    assert field2.name == "fieldTwo"
