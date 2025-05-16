from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Generator, Iterator, List, Literal, Optional, Union


@dataclass
class HasProtoModule:
    protofile: str
    package: Optional[str]

    def __post_init__(self) -> None:
        self.protofile = f'{self.protofile.removesuffix(".proto")}.proto'


@dataclass
class HasMeta:
    comment: str
    options: Dict[str, Union[str, bool]]


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
        )


def validate_service(block: "Block") -> None:
    for f in block.fields:
        if not isinstance(f, Method):
            raise TypeError(
                f'Service Block should have Methods only. Found "{type(f)}" for field "{getattr(f, "name", "?")}" in block "{block.name}"'
            )


def validate_enum(block: "Block") -> None:
    for f in block.fields:
        if not isinstance(f, Field):
            raise TypeError(
                f"Enum Block should have Field only. Found {type(f)} in block '{block.name}'"
            )
        if f.ftype:
            raise TypeError(
                f'Enum Field should have no type. Found "{f.ftype}" on field "{f.name}" in block "{block.name}"'
            )


def validate_message(block: "Block") -> None:
    for f in block.fields:
        if isinstance(f, Method):
            raise TypeError(
                f"Message Block '{block.name}' should not have Methods. Found method: {f.method_name}"
            )
        if isinstance(f, Field) and not f.ftype:
            raise TypeError(
                f"Message Block '{block.name}' found no ftype for field: {f.name}"
            )


def validate_oneof(block: "Block") -> None:
    for f in block.fields:
        if not isinstance(f, Field):
            raise TypeError(
                f"Oneof Block should have Field only. Found {type(f)} in block '{block.name}'"
            )
        if not f.ftype:
            raise TypeError(
                f"Oneof Block should have a type. Found no type for field: {f.name}"
            )


validate_block = {
    "service": validate_service,
    "enum": validate_enum,
    "message": validate_message,
    "oneof": validate_oneof,
}


@dataclass
class Block(HasMeta, HasProtoModule):
    name: str
    block_type: Literal["message", "enum", "oneof", "service"]
    fields: List[Union[Field, Method, "Block"]]
    reserved_index: str
    reserved_keys: str

    def __post_init__(self) -> None:
        validate_block[self.block_type](self)

    @property
    def number(self) -> int:
        if self.block_type == "oneof":
            return min([f.number for f in self.fields])
        return 0

    def __len__(self) -> int:
        return len(self.fields)

    def __iter__(self) -> Iterator[Union[Field, Method, "Block"]]:
        return iter(self.fields)

    def __hash__(self) -> int:
        return hash(
            (
                self.protofile,
                self.package,
                self.name,
                self.block_type,
                frozenset(self.fields),
            )
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
class ProtoBlocks(HasMeta, HasProtoModule):
    blocks: List[Block] = field(default_factory=list)

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
