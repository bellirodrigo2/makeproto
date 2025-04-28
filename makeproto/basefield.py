
from typing import Any


class BaseField():
    def __init__(self, default: Any = ..., **meta: Any):
        self._default = default
        self.meta = meta

class Double(BaseField):
    pass

class Float(BaseField):
    pass

class Int32(BaseField):
    pass

class Int64(BaseField):
    pass

class UInt32(BaseField):
    pass

class UInt64(BaseField):
    pass

class SInt32(BaseField):
    pass

class SInt64(BaseField):
    pass

class Fixed32(BaseField):
    pass

class Fixed64(BaseField):
    pass

class SFixed32(BaseField):
    pass

class SFixed64(BaseField):
    pass

class Bool(BaseField):
    pass

class String(BaseField):
    pass

class Bytes(BaseField):
    pass
