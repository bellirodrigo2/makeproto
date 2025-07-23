from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Optional,
    Sequence,
    Type,
    get_args,
    get_origin,
)

import pytest
from google.protobuf.empty_pb2 import Empty

from makeproto.interface import ILabeledMethod, IMetaType, IService
from makeproto.template import ProtoTemplate, render_protofile_template
from tests.compile_helper import compile_protoc


class MetaType:
    def __init__(
        self,
        argtype: Type[Any],
        basetype: Type[Any],
        origin: Optional[Type[Any]],
        package: str,
        proto_path: str,
    ) -> None:
        self.argtype = argtype
        self.basetype = basetype
        self.origin = origin
        self.package = package
        self.proto_path = proto_path


def get_protofile_path(cls: Type[Any]) -> str:
    return cls.DESCRIPTOR.file.name


def get_package(cls: Type[Any]) -> str:
    return cls.DESCRIPTOR.file.package


Empty.package = get_package(Empty)
Empty.proto_path = get_protofile_path(Empty)


def make_metatype_from_type(
    argtype: Type[Any],
) -> IMetaType:
    origin = get_origin(argtype)
    basetype = argtype if origin is None else get_args(argtype)[0]
    package = getattr(basetype, "package", "")
    proto_path = getattr(basetype, "proto_path", "")
    return MetaType(
        argtype=argtype,
        basetype=basetype,
        origin=origin,
        package=package,
        proto_path=proto_path,
    )


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


@dataclass
class Service(IService):
    name: str = field(default="service1")
    module: str = field(default="module1")
    package: str = ""
    options: Sequence[str] = field(default_factory=list[str])
    comments: str = ""
    _methods: Sequence["LabeledMethod"] = field(default_factory=list["LabeledMethod"])

    @property
    def methods(self) -> Sequence["LabeledMethod"]:
        return self._methods

    @property
    def qual_name(self) -> str:
        if self.package:
            return f"{self.package}.{self.name}"
        return self.name


@dataclass
class LabeledMethod(ILabeledMethod):
    name: str = field(default="")
    method: Callable[..., Any] = field(default=lambda x: x)
    module: str = field(default="module1")
    service: str = field(default="service1")
    package: str = field(default="")
    options: Sequence[str] = field(default_factory=list[str])
    comments: str = field(default="")
    request_types: Sequence[Any] = field(default_factory=list[Any])
    response_types: Optional[Any] = None


@pytest.fixture
def simple_service() -> Service:
    service = Service(
        name="simple_service",
        comments="Simple Service",
        options=[],
        package="",
        module="protofile1",
        _methods=[],
    )

    unary_ping = LabeledMethod(
        name="ping",
        comments="Ping Method",
        options=[],
        request_types=[empty_instance],
        response_types=empty_instance,
        method=ping,
    )
    client_stream_ping = LabeledMethod(
        name="ping_client_stream",
        comments="Ping Method Client Stream",
        options=[],
        request_types=[empty_iterator],
        response_types=empty_instance,
        method=ping_client_stream,
    )
    server_stream_ping = LabeledMethod(
        name="server_stream_ping",
        comments="Ping Method Server Stream",
        options=[],
        request_types=[empty_instance],
        response_types=empty_iterator,
        method=ping_server_stream,
    )
    bilateral_ping = LabeledMethod(
        name="ping_bilateral",
        comments="Ping Method Bilateral",
        options=[],
        request_types=[empty_iterator],
        response_types=empty_iterator,
        method=ping_bilateral,
    )
    service._methods = [
        unary_ping,
        client_stream_ping,
        server_stream_ping,
        bilateral_ping,
    ]
    return service


def write_template(rendered: str, filename: str, expected_files: int) -> None:

    with TemporaryDirectory() as temp_dir:
        proto_path = Path(temp_dir).resolve()

        filename = f"{filename}.proto"
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
        created_files = list(proto_path.rglob("*"))
        assert len(created_files) == expected_files
