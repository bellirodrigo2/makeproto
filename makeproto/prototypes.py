
from dataclasses import dataclass
from typing import Any

class BaseProto:
    @classmethod
    def prototype(cls) -> str:
        raise NotImplementedError("Subclasses should implement 'prototype'.")


class BaseMessage(BaseProto):
    __proto_file__: str = ''

    @classmethod
    def prototype(cls) -> str:
        return cls.__name__


class BaseField(BaseProto):
    def __init__(self, default: Any = ..., **meta: Any):
        self._default = default
        self.meta = meta

class Double(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "double"


class Float(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "float"


class Int32(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "int32"


class Int64(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "int64"


class UInt32(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "uint32"


class UInt64(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "uint64"


class SInt32(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "sint32"


class SInt64(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "sint64"


class Fixed32(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "fixed32"


class Fixed64(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "fixed64"


class SFixed32(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "sfixed32"


class SFixed64(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "sfixed64"


class Bool(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "bool"


class String(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "string"


class Bytes(BaseField):
    @classmethod
    def prototype(cls) -> str:
        return "bytes"
