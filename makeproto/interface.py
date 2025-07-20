from typing_extensions import Set

from typing_extensions import Any, Callable, Sequence, Optional, Protocol, Type


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
    options: Sequence[str]
    comments: str
    request_types: Sequence[IMetaType]
    response_types: Optional[IMetaType]


class IService(Protocol):
    name: str
    module: str
    package: str
    options: Sequence[str]
    comments: str

    @property
    def methods(self) -> Sequence[ILabeledMethod]: ...
    
    @property
    def qual_name(self)->str:...


class IProtoPackage(Protocol):
    package: str
    filename: str
    content: str
    depends: Set[str]
