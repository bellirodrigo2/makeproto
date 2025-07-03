from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from makeproto.compiler import CompilerContext, CompilerPass
from makeproto.interface import IService
from makeproto.make_service_template import make_service_template
from makeproto.setters.comment import CommentSetter
from makeproto.setters.imports import ImportsSetter
from makeproto.setters.name import NameSetter
from makeproto.setters.service import ServiceSetter
from makeproto.setters.type import TypeSetter
from makeproto.template import ProtoTemplate, ServiceTemplate, render_protofile_template
from makeproto.validators.comment import CommentsValidator
from makeproto.validators.custommethod import CustomPass
from makeproto.validators.imports import ImportsValidator
from makeproto.validators.name import BlockNameValidator, FieldNameValidator
from makeproto.validators.type import TypeValidator


class CompilationError(Exception):
    def __init__(self, contexts: List[CompilerContext]) -> None:
        self.contexts = contexts
        self.total_errors = sum(len(ctx) for ctx in contexts)
        super().__init__(
            f"Compilation failed with {self.total_errors} errors across {len(self.contexts)} packages."
        )


def extract_module_list(
    services: List[IService],
) -> List[str]:
    return list(set([service.module for service in services]))


def make_compiler_context(
    packlist: List[IService],
    version: int = 3,
) -> Optional[Tuple[List[ProtoTemplate], CompilerContext]]:

    if len(packlist) == 0:
        return None

    allmodules: List[ProtoTemplate] = []
    state: Dict[str, ProtoTemplate] = {}
    module_list = extract_module_list(packlist)
    package_name = packlist[0].package

    for module in module_list:
        module_template = ProtoTemplate(
            comments="",
            syntax=version,
            module=module,
            package=package_name,
            imports=set(),
            services=[],
            options=[],
        )
        state[module] = module_template
        allmodules.append(module_template)

    ctx = CompilerContext(name=package_name, state=state)
    return allmodules, ctx


def make_templates(
    packlist: List[IService],
    extract_requests: Callable[..., List[Type[Any]]],
    extract_response: Callable[..., Type[Any]],
) -> List[ServiceTemplate]:
    return [
        make_service_template(service, extract_requests, extract_response)
        for service in packlist
    ]


def run_compiler_passes(
    packs: List[Tuple[List[ServiceTemplate], CompilerContext]],
    compilerpass: List[CompilerPass],
) -> None:
    ctxs = [ctx for _, ctx in packs]
    for cpass in compilerpass:
        for block, ctx in packs:
            cpass.execute(block, ctx)

        total_errors = sum(len(ctx) for ctx in ctxs)
        if total_errors > 0:
            raise CompilationError(ctxs)


def prepare_modules(
    services: Dict[str, List[IService]],
    extract_requests: Callable[..., List[Type[Any]]],
    extract_response: Callable[..., Type[Any]],
    version: int = 3,
) -> Tuple[List[ProtoTemplate], List[Tuple[List[ServiceTemplate], CompilerContext]]]:

    all_templates: List[ProtoTemplate] = []
    compiler_execution: List[Tuple[List[ServiceTemplate], CompilerContext]] = []

    for _, service_list in services.items():
        compiler_ctx = make_compiler_context(service_list, version)
        if compiler_ctx is None:
            continue
        allmodules, ctx = compiler_ctx
        all_templates.extend(allmodules)
        templates = make_templates(service_list, extract_requests, extract_response)
        compiler_execution.append((templates, ctx))

    return all_templates, compiler_execution


def compile_service_internal(
    services: Dict[str, List[IService]],
    extract_requests: Callable[..., List[Type[Any]]],
    extract_response: Callable[..., Type[Any]],
    compilerpasses: List[List[CompilerPass]],
    version: int = 3,
) -> Optional[Dict[str, Dict[str, str]]]:

    all_templates, compiler_execution = prepare_modules(
        services, extract_requests, extract_response, version
    )
    try:
        for compilerpass in compilerpasses:
            run_compiler_passes(compiler_execution, compilerpass)
    except CompilationError as e:
        for ctx in e.contexts:
            if ctx.has_errors():
                ctx.show()
        return None

    protos_dict: Dict[str, Dict[str, str]] = defaultdict(dict)

    for template in all_templates:
        module_dict = template.to_dict()
        if not module_dict:
            continue
        rendered = render_protofile_template(module_dict)
        protos_dict[template.package][template.module] = rendered

    return protos_dict


def make_validators(
    custompassmethod: Callable[[Any], List[str]] = lambda x: [],
) -> List[CompilerPass]:

    custompass = CustomPass(visitmethod=custompassmethod)

    return [
        TypeValidator(),
        BlockNameValidator(),
        ImportsValidator(),
        FieldNameValidator(),
        CommentsValidator(),
        custompass,
    ]


def make_setters(
    get_protofile_path: Callable[[Type[Any]], str],
    get_package: Callable[[Type[Any]], str],
    maxchar_per_line: int = 80,
    always_format: bool = True,
) -> List[CompilerPass]:

    setters: List[CompilerPass] = [
        ServiceSetter(),
        TypeSetter(get_package),
        NameSetter(),
        ImportsSetter(get_protofile_path),
        CommentSetter(maxchar_per_line, always_format),
    ]
    return setters


def compile_service(
    services: Dict[str, List[IService]],
    extract_requests: Callable[..., List[Type[Any]]],
    extract_response: Callable[..., Type[Any]],
    get_protofile_path: Callable[[Type[Any]], str],
    get_package: Callable[[Type[Any]], str],
    custompassmethod: Callable[[Any], List[str]] = lambda x: [],
    maxchar_per_line: int = 80,
    always_format: bool = True,
    version: int = 3,
) -> Optional[Dict[str, Dict[str, str]]]:

    validators = make_validators(custompassmethod)
    setters = make_setters(
        get_protofile_path, get_package, maxchar_per_line, always_format
    )

    return compile_service_internal(
        services,
        extract_requests,
        extract_response,
        [validators, setters],
        version,
    )
