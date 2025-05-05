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

    def getinstance(self, tgttype: type[T], default: bool = True) -> Optional[T]:
        if self.extras is not None:
            founds = [e for e in self.extras if isinstance(e, tgttype)]
            if len(founds) > 0:
                return founds[0]
        if default and self.has_default and isinstance(self.default, tgttype):
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


def dataclass_field_factory(
    field: Field[Any], hint: Any, bt_default_fallback: bool = True
) -> FuncArg:
    name = field.name

    has_default, default = resolve_default(field)

    argtype = hint  # or (type(default) if default not in (NO_DEFAULT, None) else None)

    if argtype is None and bt_default_fallback:
        argtype = type(default) if default not in (NO_DEFAULT, None) else None

    basetype = argtype
    extras = None

    if get_origin(hint) is Annotated:
        basetype, *extras_ = get_args(hint)
        extras = tuple(extras_)

    # adicionar flag de fallback de basetype para default ?

    return FuncArg(
        name=name,
        argtype=argtype,
        basetype=basetype,
        default=default,
        has_default=has_default,
        extras=extras,
    )


def get_dataclass_fields(
    cls: type, bt_default_fallback: bool = True
) -> Sequence[FuncArg]:
    if not is_dataclass(cls):
        raise TypeError(f"{cls.__name__} is not a dataclass.")  # type: ignore

    hints = get_type_hints(
        cls, globalns=vars(sys.modules[cls.__module__]), include_extras=True
    )
    result: list[FuncArg] = []

    for field in fields(cls):
        hint: Optional[type[Any]] = hints.get(field.name, None)
        arg = dataclass_field_factory(field, hint, bt_default_fallback)
        result.append(arg)

    return result
