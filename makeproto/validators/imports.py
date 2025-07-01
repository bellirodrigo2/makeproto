from makeproto.compiler import CompilerPass
from makeproto.template import ServiceTemplate


class ImportsValidator(CompilerPass):

    def visit_service(self, block: ServiceTemplate) -> None:
        pass
