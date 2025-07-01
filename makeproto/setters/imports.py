from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Callable, Optional, Type, get_args, get_origin

from makeproto.compiler import CompilerPass
from makeproto.report import CompileErrorCode, CompileReport
from makeproto.template import MethodTemplate, ProtoTemplate, ServiceTemplate


def if_stream_get_type(bt: Type[Any]) -> Optional[type[Any]]:
    if get_origin(bt) is AsyncIterator:
        return get_args(bt)[0]
    return bt


def get_func_arg(bt: Type[Any]) -> Type[Any]:
    basetype = if_stream_get_type(bt)
    return basetype or bt


class ImportsSetter(CompilerPass):

    def __init__(
        self,
        get_class_metadata: Callable[[Type[Any]], Path],
        # proto_path: Optional[Path] = None,
    ) -> None:
        super().__init__()
        self.get_class_metadata = get_class_metadata

    def visit_service(self, block: ServiceTemplate) -> None:
        for field in block.methods:
            field.accept(self)

    def _get_imports(self, ftype: Type[Any]) -> str:

        ftype_proto = self.get_class_metadata(ftype)
        # import_path = ftype_proto.relative_to(self.proto_path)
        # import_str = import_path.as_posix()
        return str(ftype_proto)

    def _set_imports(self, field: MethodTemplate, ftype: Type[Any]) -> None:
        try:
            import_str = self._get_imports(ftype)
            module: ProtoTemplate = self.ctx.get_state(field.service.module)
            module.imports.add(import_str)
        except Exception as e:
            report: CompileReport = self.ctx.get_report(field.service)
            report.report_error(
                CompileErrorCode.SETTER_PASS_ERROR,
                field.name,
                f"ImportsSetter: {str(e)}",
            )

    def visit_method(self, method: MethodTemplate) -> None:

        request_type = get_func_arg(method.request_types[0])
        self._set_imports(method, request_type)
        response_type = get_func_arg(method.response_type)
        self._set_imports(method, response_type)
