from dataclasses import dataclass
from functools import partial
from typing import Generator, Set

from typing_extensions import Any, Callable, Dict, List, Optional, Tuple

from makeproto.compiler import CompilerContext, CompilerPass
from makeproto.format_comment import format_comment
from makeproto.interface import IProtoPackage, IService
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
from makeproto.validators.name import (
    BlockNameValidator,
    FieldNameValidator,
    check_valid,
    check_valid_filename,
)
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

    class PackageBlock:
        def __init__(self, name: str) -> None:
            self.name = f"Package<{name}>"

    report = ctx.get_report(PackageBlock(package_name))
    if package_name:
        check_valid(package_name, report)
    check_valid_filename([f"{f}.proto" for f in module_list], report)


    return allmodules, ctx


def make_templates(
    packlist: List[IService],
) -> List[ServiceTemplate]:
    return [make_service_template(service) for service in packlist]


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
        templates = make_templates(service_list)
        compiler_execution.append((templates, ctx))

    return all_templates, compiler_execution


@dataclass
class ProtoPackage(IProtoPackage):
    package: str
    filename: str
    content: str
    depends: Set[str]

    @property
    def qual_name(self) -> str:
        file_path = f"{self.filename}.proto"
        if self.package:
            pack = self.package.replace(".", "/")
            file_path = f"{pack}/{file_path}"
        return file_path


def compile_service_internal(
    services: Dict[str, List[IService]],
    compilerpasses: List[List[CompilerPass]],
    version: int = 3,
) -> Optional[Generator[IProtoPackage, None, None]]:

    all_templates, compiler_execution = prepare_modules(services, version)
    try:
        for compilerpass in compilerpasses:
            run_compiler_passes(compiler_execution, compilerpass)
    except CompilationError as e:
        for ctx in e.contexts:
            if ctx.has_errors():
                ctx.show()
        return None

    def generate_protos() -> Generator[IProtoPackage, None, None]:
        for template in all_templates:
            module_dict = template.to_dict()
            if not module_dict:
                continue
            rendered = render_protofile_template(module_dict)
            yield ProtoPackage(
                template.package, template.module, rendered, template.imports
            )

    return generate_protos()


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


default_format = partial(format_comment, max_chars=80, always_format=True)


def make_setters(
    name_normalizer: Callable[[str], str] = lambda x: x,
    format_comment: Callable[[str], str] = default_format,
) -> List[CompilerPass]:

    setters: List[CompilerPass] = [
        ServiceSetter(),
        TypeSetter(),
        NameSetter(name_normalizer),
        ImportsSetter(),
        CommentSetter(format_comment),
    ]
    return setters


def compile_service(
    services: Dict[str, List[IService]],
    name_normalizer: Callable[[str], str] = lambda x: x,
    format_comment: Callable[[str], str] = lambda x: x,
    custompassmethod: Callable[[Callable[..., Any]], List[str]] = lambda x: [],
    version: int = 3,
) -> Optional[Generator[IProtoPackage, None, None]]:

    validators = make_validators(custompassmethod)
    setters = make_setters(
        name_normalizer=name_normalizer, format_comment=format_comment
    )

    return compile_service_internal(
        services,
        [validators, setters],
        version,
    )
