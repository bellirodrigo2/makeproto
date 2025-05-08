from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar, Union

T = TypeVar("T")


@dataclass
class HasComment:
    comment: str


@dataclass
class HasOptions:
    options: Dict[str, Union[str, bool]]


@dataclass
class Field(HasComment, HasOptions):
    type: str
    name: str
    number: int

    @classmethod
    def make(
        cls,
        name: str,
        number: int,
        type_: str = "",
        comment: Optional[str] = None,
        options: Optional[Dict[str, Union[str, bool]]] = None,
    ):
        return cls(
            type=type_, name=name, number=number, comment=comment or '', options=options or {}
        )


@dataclass
class Method(HasComment, HasOptions):
    method_name: str
    request_type: str
    response_type: str
    request_stream: bool
    response_stream: bool

    @classmethod
    def make(
        cls,
        method_name: str,
        request_type: str,
        response_type: str,
        request_stream: bool,
        response_stream: bool,
        comment: str = "",
        options: Optional[Dict[str, Union[str, bool]]] = None,
    ):
        return cls(
            method_name=method_name,
            request_type=request_type,
            response_type=response_type,
            request_stream=request_stream,
            response_stream=response_stream,
            comment=comment,
            options=options or {},
        )


@dataclass
class Block(Generic[T], HasComment, HasOptions):
    name: str
    block_type: str  # message, enum, oneof, service
    fields: List[T]

    @classmethod
    def make(
        cls,
        name: str,
        block_type: Literal["message", "enum", "oneof", "service"],
        fields: List[Any],
        comment: Optional[str] = None,
        options: Optional[Dict[str, Union[str, bool]]] = None,
    ):
        return cls(
            name=name,
            block_type=block_type,
            fields=fields,
            comment=comment or '',
            options=options or {},
        )


EnumBlock = Block[Field]
OneOfBlock = Block[Field]
MessageBlock = Block[Union[Field, OneOfBlock]]
ServiceBlock = Block[Method]


@dataclass
class ProtoFile(HasComment, HasOptions):
    version: str
    package_name: str
    blocks: List[Block[Union[Field, Method]]]

    @classmethod
    def make(
        cls,
        version: int,
        package_name: str,
        blocks: List[Block[Union[Field, Method]]],
        comment: str = "",
        options: Optional[Dict[str, Union[str, bool]]] = None,
    ):
        return cls(
            version=str(version),
            package_name=package_name,
            blocks=blocks,
            comment=comment,
            options=options or {},
        )
