from typing import Any, Callable, List, Optional, Type

from typing_extensions import get_args, get_origin

from makeproto.interface import IMetaType
from makeproto.template import MethodTemplate, ServiceTemplate


def make_service(
    name: str,
    package: str = "",
    module: str = "",
    comments: str = "",
    options: Optional[List[str]] = None,
    methods: Optional[List[MethodTemplate]] = None,
) -> ServiceTemplate:
    service_template = ServiceTemplate(
        name=name,
        package=package,
        module=module,
        comments=comments,
        options=options or [],
        methods=methods or [],
    )
    return service_template


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


def make_method(
    name: str,
    method: Optional[Callable[..., Any]] = None,
    service: Optional[ServiceTemplate] = None,
    requests: Optional[List[Type[Any]]] = None,
    response: Optional[Type[Any]] = None,
    comments: str = "",
    options: Optional[List[str]] = None,
    request_stream: bool = False,
    response_stream: bool = False,
) -> MethodTemplate:

    service = service or make_service("mock_service")

    if requests is None:
        requests_ = []
    else:
        requests_ = [make_metatype_from_type(req) for req in requests]

    if response is None:
        response_ = None
    else:
        response_ = make_metatype_from_type(response)

    method_template = MethodTemplate(
        method_func=method,
        name=name,
        options=options or [],
        comments=comments,
        request_types=requests_,
        response_type=response_,
        service=service,
        request_stream=request_stream,
        response_stream=response_stream,
    )
    service.methods.append(method_template)
    return method_template
