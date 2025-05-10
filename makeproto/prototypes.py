from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, Generic, Optional, TypeVar, Union


class BaseProto:
    @classmethod
    def prototype(cls) -> str:
        raise NotImplementedError("Subclasses should implement 'prototype'.")


class ProtoHeader:
    __proto_file__: str
    __proto_package__: str

    @classmethod
    def protofile(cls)->str:
        return f'{cls.__proto_file__.rstrip('.proto')}.proto'

    @classmethod
    def package(cls)->str:
        return cls.__proto_package__


class BaseMessage(BaseProto,ProtoHeader):

    _oneof: dict[str, set[str]]
    _selected: dict[str, str]

    @classmethod
    def prototype(cls) -> str:
        return cls.__name__
    
    @classmethod
    def qualified_prototype(cls) -> str:
        return f'{cls.package()}.{cls.__name__}'
    

class BaseField(BaseProto):
    pass


class BaseStringField(str, BaseField):
    @classmethod
    def python_type(cls) -> type[str]:
        return str


class BaseIntField(int, BaseField):
    @classmethod
    def python_type(cls) -> type[int]:
        return int


class BaseFloatField(float, BaseField):
    @classmethod
    def python_type(cls) -> type[float]:
        return float


class BaseBytesField(bytes, BaseField):
    @classmethod
    def python_type(cls) -> type[bytes]:
        return bytes


class BaseBoolField(BaseField):
    def __init__(self, value: bool = False) -> None:
        self._value = bool(value)

    def __bool__(self) -> bool:
        return self._value

    def __repr__(self) -> str:
        return str(self._value)

    @classmethod
    def python_type(cls) -> type[bool]:
        return bool


class Double(BaseFloatField):
    @classmethod
    def prototype(cls) -> str:
        return "double"


class Float(BaseFloatField):
    @classmethod
    def prototype(cls) -> str:
        return "float"


class Int32(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "int32"


class Int64(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "int64"


class UInt32(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "uint32"


class UInt64(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "uint64"


class SInt32(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "sint32"


class SInt64(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "sint64"


class Fixed32(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "fixed32"


class Fixed64(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "fixed64"


class SFixed32(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "sfixed32"


class SFixed64(BaseIntField):
    @classmethod
    def prototype(cls) -> str:
        return "sfixed64"


class Bool(BaseBoolField):
    @classmethod
    def prototype(cls) -> str:
        return "bool"


class String(BaseStringField):
    @classmethod
    def prototype(cls) -> str:
        return "string"


class Bytes(BaseBytesField):
    @classmethod
    def prototype(cls) -> str:
        return "bytes"


DEFAULT_PRIMITIVES: dict[type[Any], str] = {
    str: String.prototype(),
    int: Int64.prototype(),
    float: Float.prototype(),
    bytes: Bytes.prototype(),
    bool: Bool.prototype(),
}


class Enum(ProtoHeader,IntEnum):
    pass


T = TypeVar("T")


class OneOf(BaseField, Generic[T]): ...


class EnumOption:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class FieldSpec:
    options: Optional[Dict[str, Union[str, bool, EnumOption]]] = None
    comment: Optional[str] = None


@dataclass
class OneOfKey:
    key: str
    spec: Optional[FieldSpec] = None
