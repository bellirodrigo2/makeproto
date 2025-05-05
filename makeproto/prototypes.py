import enum
from typing import Generic, TypeVar


class BaseProto:
    @classmethod
    def prototype(cls) -> str:
        raise NotImplementedError("Subclasses should implement 'prototype'.")


class BaseMessage(BaseProto):
    __proto_file__: str = ""
    __proto_package__: str = ""

    @classmethod
    def prototype(cls) -> str:
        return cls.__name__


class BaseField(BaseProto):
    pass


class BaseStringField(str, BaseField):
    @classmethod
    def python_type(cls):
        return str


class BaseIntField(int, BaseField):
    @classmethod
    def python_type(cls):
        return int


class BaseFloatField(float, BaseField):
    @classmethod
    def python_type(cls):
        return float


class BaseBytesField(bytes, BaseField):
    @classmethod
    def python_type(cls):
        return bytes


class BaseBoolField(BaseField):
    def __init__(self, value: bool = False):
        self._value = bool(value)

    def __bool__(self):
        return self._value

    def __repr__(self):
        return str(self._value)

    @classmethod
    def python_type(cls):
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


class Enum(BaseMessage, enum.Enum): ...


T = TypeVar("T")


class OneOf(BaseField, Generic[T]): ...


class OneOfKey(str):
    def __new__(cls, value):
        if not isinstance(value, str):
            raise TypeError(
                f"{cls.__name__} wait a str, but got {type(value).__name__}"
            )
        return str.__new__(cls, value)


# messagebuilder tem que checar se tem outros nomes
# package nao pode ter mesmo nome de message
