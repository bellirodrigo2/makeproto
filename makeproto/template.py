from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from typing_extensions import Any, Callable, Dict, List, Optional, Protocol, Set, Type

from makeproto.interface import IMetaType


class Visitor(Protocol):
    def visit_service(self, block: "ServiceTemplate") -> None: ...
    def visit_method(self, method: "MethodTemplate") -> None: ...


class ToDict(Protocol):
    def to_dict(self) -> Dict[str, Any]: ...


@dataclass
class Node:
    name: str
    comments: str
    options: List[str]

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError()


@dataclass
class MethodTemplate(Node, ToDict):
    service: "ServiceTemplate"

    method_func: Callable[..., Any]
    name: str
    request_types: List[IMetaType]
    response_type: Optional[IMetaType]
    request_stream: bool = False
    response_stream: bool = False

    request_str: Optional[str] = None
    response_str: Optional[str] = None

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_method(self)

    def to_dict(self) -> Dict[str, Any]:
        self_dict: Dict[str, Any] = {}

        self_dict["name"] = self.name
        self_dict["comment"] = self.comments

        self_dict["options"] = self.options

        self_dict["request_type"] = self.request_str
        self_dict["response_type"] = self.response_str

        self_dict["request_stream"] = self.request_stream
        self_dict["response_stream"] = self.response_stream

        return self_dict


@dataclass
class ServiceTemplate(Node, ToDict):
    package: str
    module: str
    methods: List[MethodTemplate]

    def __hash__(self) -> int:
        return hash((self.package, self.module, self.name))

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_service(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServiceTemplate):
            return NotImplemented
        return (
            self.package == other.package
            and self.module == other.module
            and self.name == other.name
        )

    def to_dict(self) -> Dict[str, Any]:
        self_dict: Dict[str, Any] = {}
        if not self.methods:
            return self_dict

        self_dict["service_name"] = self.name
        self_dict["service_comment"] = self.comments
        self_dict["options"] = self.options

        methods_dict: List[Dict[str, Any]] = []
        for method in self.methods:
            method_dict = method.to_dict()
            if not method_dict:
                continue
            methods_dict.append(method_dict)
        self_dict["methods"] = methods_dict

        return self_dict


@dataclass
class ProtoTemplate(ToDict):
    comments: str
    syntax: int
    package: str
    module: str
    imports: Set[str]
    services: List[ServiceTemplate]
    options: List[str]

    def to_dict(self) -> Dict[str, Any]:
        self_dict: Dict[str, Any] = {}
        if not self.services:
            return self_dict

        self_dict["comment"] = self.comments
        self_dict["syntax"] = f"proto{self.syntax}"
        self_dict["package"] = self.package
        self_dict["imports"] = self.imports
        self_dict["options"] = self.options

        services_dict: List[Dict[str, Any]] = []
        for service in self.services:
            service_dict = service.to_dict()
            if not service_dict:
                continue
            services_dict.append(service_dict)
        self_dict["services"] = services_dict

        return self_dict


TEMPLATE_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True
)


def render_service_template(data: Dict[str, str]) -> str:
    template = env.get_template("service.j2")
    return template.render(data)


def render_protofile_template(data: Dict[str, str]) -> str:
    env.globals["render_service_template"] = render_service_template
    template = env.get_template("protofile.j2")
    return template.render(data)
