from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, AsyncIterator, Type

import pytest

from makeproto.build_service import CompilationError, make_setters, make_validators
from makeproto.compiler import CompilerContext
from makeproto.template import (
    MethodTemplate,
    ProtoTemplate,
    ServiceTemplate,
    render_protofile_template,
)
from tests.compile_helper import compile_protoc
from tests.test_helpers import make_metatype_from_type


class Base:
    pass


class Empty(Base):
    package = "google.protobuf"
    proto_path = "google/protobuf/empty.proto"


empty_instance = make_metatype_from_type(Empty)
empty_iterator = make_metatype_from_type(AsyncIterator[Empty])


async def ping(req: Empty) -> Empty:
    return Empty()


async def ping_client_stream(req: AsyncIterator[Empty]) -> Empty:
    return Empty()


async def ping_server_stream(req: Empty) -> AsyncIterator[Empty]:
    yield Empty()


async def ping_bilateral(req: AsyncIterator[Empty]) -> AsyncIterator[Empty]:
    yield Empty()


@pytest.fixture
def simple_service() -> ServiceTemplate:
    service = ServiceTemplate(
        name="simple_service",
        comments="Simple Service",
        options=[],
        package="",
        module="protofile1",
        methods=[],
    )

    unary_ping = MethodTemplate(
        name="ping",
        comments="Ping Method",
        options=[],
        request_types=[empty_instance],
        response_type=empty_instance,
        method_func=ping,
        service=service,
    )
    client_stream_ping = MethodTemplate(
        name="ping_client_stream",
        comments="Ping Method Client Stream",
        options=[],
        request_types=[empty_iterator],
        response_type=empty_instance,
        method_func=ping_client_stream,
        service=service,
    )
    server_stream_ping = MethodTemplate(
        name="server_stream_ping",
        comments="Ping Method Server Stream",
        options=[],
        request_types=[empty_instance],
        response_type=empty_iterator,
        method_func=ping_server_stream,
        service=service,
    )
    bilateral_ping = MethodTemplate(
        name="ping_bilateral",
        comments="Ping Method Bilateral",
        options=[],
        request_types=[empty_iterator],
        response_type=empty_iterator,
        method_func=ping_bilateral,
        service=service,
    )
    service.methods = [
        unary_ping,
        client_stream_ping,
        server_stream_ping,
        bilateral_ping,
    ]
    return service


def test_protofile_basic(simple_service: ServiceTemplate) -> None:
    protofile_name = "protofile1"
    protofile = ProtoTemplate(
        comments="Proto File for testing",
        package="my.package",
        module=protofile_name,
        syntax=3,
        imports=set(),
        services=[],
        options=[],
    )
    ctx = CompilerContext(state={protofile_name: protofile})

    validators = make_validators()
    setters = make_setters()
    compilerpasses = [validators, setters]
    blocks = [simple_service]

    for compilerpass in compilerpasses:
        for cpass in compilerpass:
            cpass.execute(blocks, ctx)

        total_errors = len(ctx)
        if total_errors > 0:
            ctx.show()
            raise CompilationError([])
    protofile_dict = protofile.to_dict()

    rendered = render_protofile_template(protofile_dict)

    with TemporaryDirectory() as temp_dir:
        proto_path = Path(temp_dir).resolve()

        filename = "protofile.proto"
        with open(proto_path / filename, "w", encoding="utf-8") as f:
            f.write(rendered)

        output_dir = proto_path / "compiled"
        output_dir.mkdir(exist_ok=True)
        compile_protoc(
            proto_path=proto_path,
            protofile=filename,
            output_dir=output_dir,
            add_google=True,
        )
        assert len(list(proto_path.rglob("*"))) == 4
