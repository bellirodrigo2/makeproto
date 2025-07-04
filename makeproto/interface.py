from pathlib import Path

from typing_extensions import Any, Callable, List, Optional, Protocol, Type


class IMetaType(Protocol):
    argtype: Type[Any]
    basetype: Type[Any]
    origin: Optional[Type[Any]]
    package: str
    proto_path: str


class ILabeledMethod(Protocol):
    method: Callable[..., Any]
    package: str
    module: str
    service: str
    options: List[str]
    comments: str
    request_types: List[IMetaType]
    response_types: Optional[IMetaType]


class IService(Protocol):
    name: str
    module: str
    package: str
    options: List[str]
    comments: str

    @property
    def methods(self) -> List[ILabeledMethod]: ...


class IMessageDefinition(Protocol):
    msg_base_class: Any
    instance_class: Type[Any]
    get_package: Callable[[Type[Any]], str]
    get_protofile_path: Callable[[Type[Any]], Path]
