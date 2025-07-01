import inspect
from collections.abc import AsyncIterator
from typing import Any, Callable, List, Optional, Type, get_args, get_origin

from makeproto.compiler import CompilerPass
from makeproto.report import CompileErrorCode, CompileReport
from makeproto.template import MethodTemplate, ServiceTemplate


def is_async_func(func: Callable[..., Any]) -> bool:
    return inspect.isasyncgenfunction(func)


def if_stream_get_type(bt: Type[Any]) -> Optional[type[Any]]:
    if get_origin(bt) is AsyncIterator:
        return get_args(bt)[0]
    return None


class TypeValidator(CompilerPass):

    def visit_service(self, block: ServiceTemplate) -> None:
        for field in block.methods:
            field.accept(self)

    def _check_requests(
        self, name: str, report: CompileReport, requests: List[type[Any]]
    ) -> None:
        msg = None
        invalid_req = CompileErrorCode.METHOD_INVALID_REQUEST_TYPE
        if len(requests) == 0:
            msg = "Method must define a request message."
        elif len(requests) > 1:
            sets = set(map(lambda x: if_stream_get_type(x), requests))
            if len([v for v in sets if v is not None]) == 1:
                msg = "Stream and Single request mixed in the args"
            else:
                msg = f"Only one request message allowed per method. Found {[req.__name__ for req in requests]}"
        if msg is not None:
            report.report_error(code=invalid_req, location=name, override_msg=msg)

    def _check_response(self, method: MethodTemplate) -> None:
        report: CompileReport = self.ctx.get_report(method.service)
        if method.response_type is None:
            override_msg = None
            if method.response_type is None:
                override_msg = "Response type is 'None'"
            report.report_error(
                CompileErrorCode.METHOD_INVALID_RESPONSE_TYPE,
                location=method.name,
                override_msg=override_msg,
            )
        is_func_async = is_async_func(method.method_func)
        is_return_async = if_stream_get_type(method.response_type) is not None
        consistency = is_return_async == is_func_async
        if not consistency:
            report.report_error(
                code=CompileErrorCode.METHOD_NOT_CONSISTENT_TO_RETURN,
                location=method.name,
            )

    def visit_method(self, method: MethodTemplate) -> None:
        report: CompileReport = self.ctx.get_report(method.service)
        self._check_requests(method.name, report, method.request_types)
        self._check_response(method)
