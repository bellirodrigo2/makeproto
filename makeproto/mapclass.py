import sys
from dataclasses import MISSING, Field, dataclass, fields, is_dataclass
from typing import (
    Annotated,
    Any,
    Optional,
    Sequence,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from makeproto.prototypes import (
    BaseField,
    BaseProto,
    Bool,
    Bytes,
    Float,
    Int64,
    OneOf,
    OneOfKey,
    String,
)

T = TypeVar("T")


@dataclass(frozen=True)
class FuncArg:
    name: str
    argtype: Optional[type[Any]]
    basetype: Optional[type[Any]]
    default: Optional[Any]
    has_default: bool = False
    extras: Optional[tuple[Any]] = None

    @property
    def origin(self) -> Optional[type[Any]]:
        return get_origin(self.basetype)

    @property
    def args(self) -> tuple[Any, ...]:
        return get_args(self.basetype)

    def getinstance(self, tgttype: type[T]) -> Optional[T]:
        if self.extras is not None:
            founds = [e for e in self.extras if isinstance(e, tgttype)]
            if len(founds) > 0:
                return founds[0]
        if self.has_default and isinstance(self.default, tgttype):
            return self.default
        return None

    def hasinstance(self, tgttype: type) -> bool:
        return False if self.getinstance(tgttype) is None else True


NO_DEFAULT = object()


def resolve_default(field: Field[Any]):
    if field.default is not MISSING:
        default = field.default
        has_default = True
    elif field.default_factory is not MISSING:
        default = field.default_factory  # armazena a fábrica, sem chamar
        has_default = True
    else:
        default = NO_DEFAULT
        has_default = False
    return has_default, default


def dataclass_field_factory(field: Field[Any], hint: Any) -> FuncArg:
    name = field.name

    has_default, default = resolve_default(field)

    argtype = hint or (type(default) if default not in (NO_DEFAULT, None) else None)
    basetype = argtype
    extras = None

    if get_origin(hint) is Annotated:
        basetype, *extras_ = get_args(hint)
        extras = tuple(extras_)

    return FuncArg(
        name=name,
        argtype=argtype,
        basetype=basetype,
        default=default,
        has_default=has_default,
        extras=extras,
    )


def get_dataclass_fields(cls: type) -> Sequence[FuncArg]:
    if not is_dataclass(cls):
        raise TypeError(f"{cls.__name__} is not a dataclass.")  # type: ignore

    hints = get_type_hints(
        cls, globalns=vars(sys.modules[cls.__module__]), include_extras=True
    )
    result: list[FuncArg] = []

    for field in fields(cls):
        hint: Optional[type[Any]] = hints.get(field.name, None)
        arg = dataclass_field_factory(field, hint)
        result.append(arg)

    return result


def get_type(bt: Optional[type[Any]]) -> Optional[str]:

    if bt is None or not isinstance(bt, type):  # type: ignore
        return None

    if issubclass(bt, BaseProto):  # type: ignore
        return bt.prototype()

    def get_default(bt: type[Any]) -> Optional[str]:

        bclass: Optional[type[BaseField]] = None
        if issubclass(bt, int):
            bclass = Int64
        if issubclass(bt, float):
            bclass = Float
        if issubclass(bt, str):
            bclass = String
        if issubclass(bt, bytes):
            bclass = Bytes
        if issubclass(bt, bool):
            bclass = Bool
        if bclass is not None:
            return bclass.prototype()
        return None

    return get_default(bt)


allowed_map_key = [
    "int32",
    "int64",
    "uint32",
    "uint64",
    "sint32",
    "sint64",
    "fixed32",
    "fixed64",
    "sfixed32",
    "sfixed64",
    "bool",
    "string",
]


def get_type_str(arg: FuncArg) -> Optional[str]:

    bt = arg.basetype
    origin = arg.origin
    args = arg.args

    if origin in {list, set}:
        type_str = get_type(args[0])
        if type_str is None:
            return None
        return f"repeated {type_str}"

    if origin is dict:
        key_type, value_type = args
        key_type_str = get_type(key_type)
        value_type_str = get_type(value_type)

        if (
            key_type_str is None
            or value_type_str is None
            or key_type_str not in allowed_map_key
        ):
            return None

        return f"map<{key_type_str}, {value_type_str}>"

    return get_type(bt)


def get_oneof_details(arg: FuncArg) -> Optional[tuple[OneOfKey, str, Any]]:

    oneofkey = arg.getinstance(OneOfKey)

    if not arg.origin is OneOf:
        if oneofkey is not None:
            raise Exception("tem oneofkey mas nao é oneof")
        return None

    if oneofkey is None:
        raise Exception("falta oneofkey")

    args = arg.args
    str_type = get_type(args[0])
    if str_type is None:
        raise TypeError(f"OneOf type is not allowed {type(args[0])}")

    return oneofkey, arg.name, str_type
