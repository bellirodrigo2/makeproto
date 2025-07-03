from typing import Any, Callable, List, Type

from makeproto.interface import IService
from makeproto.template import MethodTemplate, ServiceTemplate


def make_service_template(
    service: IService,
    extract_requests: Callable[..., List[Type[Any]]],
    extract_response: Callable[..., Type[Any]],
) -> ServiceTemplate:

    service_template = ServiceTemplate(
        name=service.name,
        package=service.package,
        module=service.module,
        comments=service.comments,
        options=service.options,
        methods=[],
    )
    methods: List[MethodTemplate] = []

    for labeledmethod in service.methods:
        method = labeledmethod.method

        requests = extract_requests(method)
        response_type = extract_response(method)

        method_template = MethodTemplate(
            method_func=method,
            name=method.__name__,
            options=labeledmethod.options,
            comments=labeledmethod.comments,
            request_types=requests,
            response_type=response_type,
            service=service_template,
            request_stream=False,
            response_stream=False,
        )
        methods.append(method_template)
    service_template.methods = methods
    return service_template
