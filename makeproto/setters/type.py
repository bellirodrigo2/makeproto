from collections.abc import AsyncIterator
from typing import Any, Callable, Optional, Tuple, Type, get_args, get_origin

from makeproto.compiler import CompilerPass
from makeproto.report import CompileErrorCode, CompileReport
from makeproto.template import MethodTemplate, ServiceTemplate


def get_type_str(bt: Type[Any], package: str) -> str:
    cls_name = bt.__name__
    if not package:
        return cls_name
    return f"{package}.{cls_name}"


def if_stream_get_type(bt: Type[Any]) -> Optional[type[Any]]:
    if get_origin(bt) is AsyncIterator:
        return get_args(bt)[0]
    return None


def get_func_arg_info(tgt: Type[Any]) -> Tuple[type[Any], bool]:
    argtype = if_stream_get_type(tgt)
    if argtype is not None:
        return argtype, True
    return tgt, False


class TypeSetter(CompilerPass):

    def __init__(
        self,
        get_class_metadata: Callable[[Type[Any]], str],
    ) -> None:
        super().__init__()
        self.get_class_metadata = get_class_metadata

    def visit_service(self, block: ServiceTemplate) -> None:
        for field in block.methods:
            field.accept(self)

    def visit_method(self, method: MethodTemplate) -> None:
        try:
            request_type, request_stream = get_func_arg_info(method.request_types[0])
            package = self.get_class_metadata(request_type)
            request_str = get_type_str(request_type, package)
            method.request_str = request_str
            method.request_stream = request_stream

            response_type, response_stream = get_func_arg_info(method.response_type)
            package = self.get_class_metadata(response_type)
            response_str = get_type_str(response_type, package)
            method.response_str = response_str
            method.response_stream = response_stream

        except Exception as e:
            report: CompileReport = self.ctx.get_report(method.service)
            report.report_error(
                CompileErrorCode.SETTER_PASS_ERROR,
                method.name,
                f"TypeSetter.visit_method: {str(e)}",
            )
