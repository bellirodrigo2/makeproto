from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Generator, Iterator, List, Literal, Optional, Set, Union

from makeproto.prototypes2 import ProtoOption


@dataclass
class ProtoModule:
    protofile: str
    package: Optional[str]

    def __post_init__(self) -> None:
        self.protofile = f'{self.protofile.rstrip(".proto")}.proto'


@dataclass
class HasMeta:
    comment: str
    options: ProtoOption


@dataclass
class Field(HasMeta):
    ftype: Optional[type[Any]]
    name: str
    number: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __hash__(self) -> int:
        return hash((self.name, self.ftype, self.number))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Field):
            return False
        return (
            self.name == other.name
            and self.ftype == other.ftype
            and self.number == other.number
        )


@dataclass
class Method(HasMeta):
    method_name: str
    request_type: type[Any]
    response_type: type[Any]
    request_stream: bool
    response_stream: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __hash__(self) -> int:
        return hash(
            (
                self.method_name,
                self.request_type.__name__,
                self.response_type.__name__,
                self.request_stream,
                self.response_stream,
            )
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Method):
            return False
        return (
            self.method_name == other.method_name
            and self.request_type.__name__ == other.request_type.__name__
            and self.response_type.__name__ == other.response_type.__name__
            and self.request_stream == other.request_stream
            and self.response_stream == other.response_stream
            and self.req_prefix == other.req_prefix
            and self.resp_prefix == other.resp_prefix
        )


@dataclass
class Block(HasMeta, ProtoModule):
    name: str
    block_type: Literal["message", "enum", "oneof", "service"]
    fields: Set[Union[Field, Method, "Block"]]
    reserved: List[str]

    def __post_init__(self) -> None:
        # checar consistencia do block_type vs dos fields...
        # se services...fields method only...
        # se enum....field only com type = ''
        # se message, fields ou oneof blocks
        # se oneof...fields only
        self.fields = frozenset(self.fields)

    def __iter__(self) -> Iterator[Union[Field, Method, "Block"]]:
        return iter(self.fields)

    def __hash__(self) -> int:
        return hash(
            (self.protofile, self.package, self.name, self.block_type, self.fields)
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Block):
            return False
        return (
            self.protofile == other.protofile
            and self.package == other.package
            and self.name == other.name
            and self.block_type == other.block_type
            and self.fields == other.fields
        )


@dataclass
class ProtoBlocks(HasMeta, ProtoModule):
    blocks: Set[Block] = field(default_factory=set)

    def __iter__(
        self,
    ) -> Iterator[Block]:
        return iter(self.blocks)

    def iter_field_names(self) -> Generator[str, Any, None]:
        for item in self.blocks:
            if isinstance(item, Field):
                yield item.name
            elif isinstance(item, Method):
                yield item.method_name
            elif isinstance(item, Block):  # type: ignore
                for field in item:
                    if isinstance(field, Field):
                        yield field.name
                    elif isinstance(field, Method):
                        yield field.method_name
            else:
                raise TypeError(
                    f'When iterating through protofile block "{self.protofile}", found an item: {type(item)}'
                )


@dataclass
class ProtoFile(ProtoBlocks):
    version: int = 3
