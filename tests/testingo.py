from enum import EnumMeta, IntEnum
from typing import Any, ClassVar, Dict, List, Tuple, Type


class ProtoMeta(type):
    def __new__(
        mcs: Type[type],
        name: str,
        bases: Tuple[Type[Any], ...],
        namespace: Dict[str, Any],
        **kwargs: Any,
    ) -> Type[Any]:
        if len(bases) > 1 and BaseMessage in bases:

            protofile = namespace.get("_proto_file", None)
            package = namespace.get("_proto_package", "")

            if protofile is None:
                raise ValueError

            existing_pack = BaseMessage._BaseMessage__file_to_package.get(
                protofile, None
            )

            if existing_pack is None:
                BaseMessage._BaseMessage__file_to_package[protofile] = package
            elif package != existing_pack:
                raise ValueError

        return super().__new__(mcs, name, bases, namespace)


class ProtoHeader:

    _comment: str = ""

    @classmethod
    def comment(cls) -> str:
        return cls._comment


class BaseMessage(ProtoHeader, metaclass=ProtoMeta):
    __file_to_package: ClassVar[dict[str, str]] = {}

    _proto_file: str
    _proto_package: str

    @classmethod
    def prototype(cls) -> str:
        return cls.__name__

    @classmethod
    def protofile(cls) -> str:
        return cls._proto_file

    @classmethod
    def package(cls) -> str:
        return cls._proto_package


class ProtoEnumMeta(ProtoMeta, EnumMeta):
    pass


class Enum(IntEnum, metaclass=ProtoEnumMeta):
    pass


class Proto1(BaseMessage):

    _proto_file = "proto1"
    _proto_package = "pack1"


class Proto2(BaseMessage):

    _proto_file = "proto2"
    _proto_package = "pack2"


class MyClass1(Proto1): ...


class MyClass2(Proto2): ...


m1 = MyClass1()
m2 = MyClass2()


class M3(Proto1, Enum):
    VAL = 0


m3 = M3.VAL

print(M3.protofile())


class Proto3(BaseMessage):

    _proto_file = "proto1"
    _proto_package = "pack2"


class EnumOpt(str): ...


s = "heelo"
t = EnumOpt("yellow")

print(isinstance(s, str))
print(isinstance(s, EnumOpt))


print(isinstance(t, str))
print(isinstance(t, EnumOpt))
