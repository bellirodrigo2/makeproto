from typing import Any, Callable, List, Optional, Type

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

    method_template = MethodTemplate(
        method_func=method,
        name=name,
        options=options or [],
        comments=comments,
        request_types=requests or [],
        response_type=response,
        service=service,
        request_stream=request_stream,
        response_stream=response_stream,
    )
    service.methods.append(method_template)
    return method_template
