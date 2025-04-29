
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
    
    @classmethod
    def python_type(cls):
        raise NotImplementedError()

class BaseStringField(str, BaseField):
    def __new__(cls, value: Any = "", *args, **kwargs):
        obj = str.__new__(cls, value)
        return obj

    def __init__(self, value: Any = "", default: Any = ..., **meta: Any):
        super().__init__(default=default, **meta)
        
    @classmethod
    def python_type(cls):
        return str

class BaseIntField(int, BaseField):
    def __new__(cls, value: Any = 0, *args, **kwargs):
        obj = int.__new__(cls, value)
        return obj

    def __init__(self, value: Any = 0, default: Any = ..., **meta: Any):
        super().__init__(default=default, **meta)

    @classmethod
    def python_type(cls):
        return int

class BaseFloatField(float, BaseField):
    def __new__(cls, value: Any = 0.0, *args, **kwargs):
        obj = float.__new__(cls, value)
        return obj

    def __init__(self, value: Any = 0.0, default: Any = ..., **meta: Any):
        super().__init__(default=default, **meta)


    @classmethod
    def python_type(cls):
        return float


class BaseBytesField(bytes, BaseField):
    def __new__(cls, value: Any = b"", *args, **kwargs):
        if isinstance(value, str):
            value = value.encode()
        obj = bytes.__new__(cls, value)
        return obj

    def __init__(self, value: Any = b"", default: Any = ..., **meta: Any):
        super().__init__(default=default, **meta)

    @classmethod
    def python_type(cls):
        return bytes

class BaseBoolField(BaseField):
    def __init__(self, value: bool = False, default: Any = ..., **meta: Any):
        super().__init__(default=default, **meta)
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
