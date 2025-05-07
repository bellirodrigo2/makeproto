from dataclasses import dataclass, field
from typing import Iterable, get_origin

from makeproto.prototypes import BaseMessage
from makeproto.templates import MethodFieldTemplate, ServiceTemplate


@dataclass
class FuncSignature:
    method_name: str
    request_type: type
    response_type: type
    client_streaming: bool
    server_streaming: bool
    options: list[str] = field(default_factory=list)

    def __post_init__(self):

        def get_error_msg(req_or_resp:str, reason:str):
            raise TypeError(f'Error on FuncSignature {req_or_resp} type for method {self.method_name}. {reason}')

        if self.request_type is None:
            get_error_msg('Request','Request type is None')

        if self.response_type is None:
            get_error_msg('Response','Response type is None')

        if not isinstance(self.request_type, type): # type: ignore
            get_error_msg('Request',f'request_type is not a type: {type(self.request_type)}')

        if not issubclass(self.request_type,BaseMessage):
            get_error_msg('Request',f'request_type is not a BaseMessage: {type(self.request_type)}')

        if not isinstance(self.response_type, type):
            get_error_msg('Response',f'response_type is not a type: {type(self.response_type)}')

        if not issubclass(self.response_type,BaseMessage):
            get_error_msg('Response',f'response_type is not a BaseMessage: {type(self.response_type)}')

        req_origin = get_origin(self.request_type)
        res_origin = get_origin(self.response_type)

        if req_origin is not None:
            get_error_msg('Request',f'request_type has an origin = "{req_origin}"')
        if  res_origin is not None:
            get_error_msg('Request',f'response_type has an origin = "{res_origin}"')


def make_service_template(service_name: str, funcs: Iterable[FuncSignature]) -> ServiceTemplate:

    methods: list[str] = []

    for func in funcs:

        temp = MethodFieldTemplate(
            method_name=func.method_name,
            request_type=func.request_type,
            response_type=func.response_type,
            client_streaming=func.client_streaming,
            server_streaming=func.server_streaming,
            options=func.options,
        )
        method = temp.build().strip("\n")
        methods.append(method)

    return ServiceTemplate(name=service_name, fields=methods)

def make_service_proto_str(service_name: str, funcs: Iterable[FuncSignature]) -> str:
    return make_service_template(service_name,funcs).build()