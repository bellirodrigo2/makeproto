from pathlib import Path
from typing import Any, Type

import pytest

from makeproto.compiler import CompilerContext
from makeproto.setters.imports import ImportsSetter
from makeproto.template import ProtoTemplate
from tests.test_helpers import make_method, make_service

proto_path: Path = Path(__file__).parent.parent.parent


def get_cls_proto_path(cls: Type[Any]) -> Path:
    ftype_proto = cls.cls_proto_path
    import_path = ftype_proto.relative_to(proto_path)
    import_str = import_path.as_posix()
    return import_str


class Mock1:
    cls_proto_path: Path = proto_path / "objects" / "user.proto"


@pytest.fixture
def context_and_template() -> tuple[CompilerContext, ProtoTemplate]:
    mod = "module1"
    block = make_service(name="TestBlock", module=mod)
    template = ProtoTemplate(
        comments="",
        syntax=3,
        package="pack1",
        module="module1",
        imports=set(),
        services=[],
        options=[],
    )
    context = CompilerContext(state={mod: template})
    return context, template, block


def test_imports_setter_ok(
    context_and_template: tuple[CompilerContext, ProtoTemplate, Any],
) -> None:
    context, template, block = context_and_template

    make_method(
        name="method1",
        requests=[Mock1],
        response=Mock1,
        service=block,
    )

    import_setter = ImportsSetter(get_cls_proto_path)
    import_setter.execute([block], context)

    assert template.imports == {"objects/user.proto"}
