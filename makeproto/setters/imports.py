from makeproto.compiler import CompilerPass
from makeproto.interface import IMetaType
from makeproto.report import CompileErrorCode, CompileReport
from makeproto.template import MethodTemplate, ProtoTemplate, ServiceTemplate


class ImportsSetter(CompilerPass):

    def visit_service(self, block: ServiceTemplate) -> None:
        for field in block.methods:
            field.accept(self)

    def _set_imports(self, field: MethodTemplate, ftype: IMetaType) -> None:
        try:
            import_str = ftype.proto_path
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

        request_type = method.request_types[0]
        self._set_imports(method, request_type)
        self._set_imports(method, method.response_type)
