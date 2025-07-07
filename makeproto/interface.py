from typing import Set

from typing_extensions import Any, Callable, List, Optional, Protocol, Type


class IMetaType(Protocol):
    argtype: Type[Any]
    basetype: Type[Any]
    origin: Optional[Type[Any]]
    package: str
    proto_path: str


class ILabeledMethod(Protocol):
    name: str
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


class IProtoPackage(Protocol):
    package: str
    filename: str
    content: str
    depends: Set[str]
