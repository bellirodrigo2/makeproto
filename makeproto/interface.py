from pathlib import Path
from typing import Any, Callable, List, Protocol, Type


class ILabeledMethod(Protocol):
    method: Callable[..., Any]
    package: str
    module: str
    service: str
    options: List[str]
    comments: str


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
