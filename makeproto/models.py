from dataclasses import asdict, dataclass
from typing import Any, Dict, Generic, List, Literal, Optional, Set, TypeVar, Union

from makeproto.prototypes import EnumOption

T = TypeVar("T")


@dataclass
class ProtoModule:
    protofile: str
    package: Optional[str]

    def __post_init__(self):
        self.protofile = f'{self.protofile.rstrip(".proto")}.proto'


@dataclass
class HasComment:
    comment: str


@dataclass
class HasOptions:
    options: Dict[str, Union[str, bool, EnumOption]]


@dataclass
class Field(HasComment, HasOptions):
    ftype: str
    name: str
    number: int

    def to_dict(self):
        return asdict(self)

    def __hash__(self):
        return hash((self.name, self.ftype, self.number))

    def __eq__(self, other: Any):

        if not isinstance(other, Field):
            return False

        return (
            self.name == other.name
            and self.ftype == other.ftype
            and self.number == other.number
        )

    @classmethod
    def make(
        cls,
        name: str,
        number: int,
        ftype: str = "",
        comment: Optional[str] = None,
        options: Optional[Dict[str, Union[str, bool, EnumOption]]] = None,
    ) -> "Field":
        return cls(
            ftype=ftype,
            name=name,
            number=number,
            comment=comment or "",
            options=options or {},
        )

@dataclass
class Field2(HasComment, HasOptions):
    ftype: type[Any]
    name: str
    number: int

    def to_dict(self):
        return asdict(self)

    def __hash__(self):
        return hash((self.name, self.ftype, self.number))

    def __eq__(self, other: Any):

        if not isinstance(other, Field2):
            return False

        return (
            self.name == other.name
            and self.ftype == other.ftype
            and self.number == other.number
        )

    @classmethod
    def make(
        cls,
        name: str,
        number: int,
        ftype: type[Any],
        comment: Optional[str] = None,
        options: Optional[Dict[str, Union[str, bool, EnumOption]]] = None,
    ) -> "Field2":
        return cls(
            ftype=ftype,
            name=name,
            number=number,
            comment=comment or "",
            options=options or {},
        )

@dataclass
class Method(HasComment, HasOptions):
    method_name: str
    request_type: type[Any]
    response_type: type[Any]
    request_stream: bool
    response_stream: bool

    req_prefix:Optional[str]=None
    resp_prefix:Optional[str]=None

    def to_dict(self):
        _asdict = asdict(self)

        _asdict["request_type"] = self.request_type.__name__
        _asdict["response_type"] = self.response_type.__name__

        return _asdict


    def __hash__(self):
        return hash(self.method_name,)

    def __eq__(self, other: Any):
        if not isinstance(other, Method):
            return False
        return self.method_name == other.method_name


    @classmethod
    def make(
        cls,
        method_name: str,
        request_type: type[Any],
        response_type: type[Any],
        request_stream: bool,
        response_stream: bool,
        comment: Optional[str] = None,
        options: Optional[Dict[str, Union[str, bool, EnumOption]]] = None,
    ) -> "Method":

        if not isinstance(request_type, type):  # type: ignore
            raise TypeError(
                f'Method "{method_name}" has inconsistent Request Type. Foud "{request_type}"'
            )

        if not isinstance(request_type, type):  # type: ignore
            raise TypeError(
                f'Method "{method_name}" has inconsistent Response Type. Foud "{response_type}"'
            )

        return cls(
            method_name=method_name,
            request_type=request_type,
            response_type=response_type,
            request_stream=request_stream,
            response_stream=response_stream,
            comment=comment or "",
            options=options or {},
        )


@dataclass
class Block(Generic[T], HasComment, HasOptions, ProtoModule):
    name: str
    block_type: Literal["message", "enum", "oneof", "service"]
    fields: List[T]

    def __iter__(self):
        return iter(self.fields)

    def __hash__(self):
        return hash(
            (
                self.protofile,
                self.name,
                self.block_type,
            )
        )

    def __eq__(self, other: Any):
        if not isinstance(other, Block):
            return False
        return (
            self.protofile == other.protofile
            and self.name == other.name
            and self.block_type == other.block_type
        )

    @classmethod
    def make(
        cls,
        protofile: str,
        package: str,
        name: str,
        block_type: Literal["message", "enum", "oneof", "service"],
        fields: List[Any],
        comment: Optional[str] = None,
        options: Optional[Dict[str, Union[str, bool, EnumOption]]] = None,
    ) -> "Block[T]":

        # TODO check blocks

        return cls(
            protofile=protofile,
            package=package,
            name=name,
            block_type=block_type,
            fields=fields,
            comment=comment or "",
            options=options or {},
        )


EnumBlock = Block[Field]
OneOfBlock = Block[Field]
MessageBlock = Block[Union[Field, OneOfBlock]]
ServiceBlock = Block[Method]


@dataclass
class ProtoFile(HasComment, HasOptions,ProtoModule):
    version: str
    imports: Set[str]
    blocks: Set[Union[EnumBlock, MessageBlock, ServiceBlock]]

    @classmethod
    def make(
        cls,
        protofile_name:str,
        package_name: Optional[str]=None,
        imports: Optional[Set[str]]=None,
        blocks: Optional[List[Union[EnumBlock, MessageBlock, ServiceBlock]]]=None,
        version: int = 3,
        comment: Optional[str] = None,
        options: Optional[Dict[str, Union[str, bool, EnumOption]]] = None,
    ) -> "ProtoFile":
        return cls(
            version=str(version),
            protofile = protofile_name,
            package=package_name,
            imports=imports or set([]),
            blocks=set(blocks or []),
            comment=comment or '',
            options=options or {},
        )
