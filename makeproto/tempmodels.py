from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Generator, Iterator, List, Literal, Optional, Set, Union


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


@dataclass
class Block(HasMeta, HasProtoModule):
    name: str
    block_type: Literal["message", "enum", "oneof", "service"]
    fields: Set[Union[Field, Method, "Block"]]
    reserved: List[str]

    def __post_init__(self) -> None:
        validate = {
            "service": self._validate_service,
            "enum": self._validate_enum,
            "message": self._validate_message,
            "oneof": self._validate_oneof,
        }.get(self.block_type)

        if not validate:
            raise ValueError(f"Invalid block_type: {self.block_type}")

        validate()
        self.fields = frozenset(self.fields)

    def _validate_service(self) -> None:
        for f in self.fields:
            if not isinstance(f, Method):
                raise TypeError(
                    f'Service Block should have Methods only. Found "{type(f)}" for field "{getattr(f, "name", "?")}" in block "{self.name}"'
                )

    def _validate_enum(self) -> None:
        for f in self.fields:
            if not isinstance(f, Field):
                raise TypeError(
                    f"Enum Block should have Field only. Found {type(f)} in block '{self.name}'"
                )
            if f.ftype:
                raise TypeError(
                    f'Enum Field should have no type. Found "{f.ftype}" on field "{f.name}" in block "{self.name}"'
                )

    def _validate_message(self) -> None:
        for f in self.fields:
            if isinstance(f, Method):
                raise TypeError(
                    f"Message Block '{self.name}' should not have Methods. Found method: {f.method_name}"
                )
            if isinstance(f, Field) and not f.ftype:
                raise TypeError(
                    f"Message Block '{self.name}' found no ftype for field: {f.name}"
                )

    def _validate_oneof(self) -> None:
        for f in self.fields:
            if not isinstance(f, Field):
                raise TypeError(
                    f"Oneof Block should have Field only. Found {type(f)} in block '{self.name}'"
                )
            if not f.ftype:
                raise TypeError(
                    f"Oneof Block should have a type. Found no type for field: {f.name}"
                )

    def __len__(self) -> int:
        return len(self.fields)

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
class ProtoBlocks(HasMeta, HasProtoModule):
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
