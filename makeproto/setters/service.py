from makeproto.compiler import CompilerPass
from makeproto.template import ProtoTemplate, ServiceTemplate


class ServiceSetter(CompilerPass):

    def visit_service(self, block: ServiceTemplate) -> None:
        module_template: ProtoTemplate = self.ctx.get_state(block.module)
        services = module_template.services
        if block in services:
            raise
        services.append(block)
