from types import ModuleType
from typing import Any, Callable, Dict, Optional

from makeproto.mapclass import FuncArg, map_model_fields
from makeproto.proxy.getters_setters import make_getter, make_kwarg, make_setter


def _get_class(
    mapcls: type[Any],
    modules: Dict[str, ModuleType],
) -> type[Any]:

    def get(modname: str, clsname: str) -> type[Any]:
        mod = modules.get(modname)
        if mod is None:
            raise KeyError(f'Module "{modname}" not found.')
        cls = getattr(mod, clsname, None)
        if cls is None:
            raise KeyError(f'Module "{modname}" has no class "{clsname}".')
        return cls

    protofile = getattr(mapcls, "protofile", None)
    if protofile is None:
        raise KeyError(f'Class "{mapcls.__name__}" has no protofile() set')
    return get(protofile(), mapcls.__name__)


def _bind_proxy(
    mapcls: type[Any],
    modules: Dict[str, ModuleType],
    make_getter: Callable[[FuncArg], Callable[[Any], Any]],
    make_setter: Callable[[FuncArg], Callable[[Any, Any], Any]],
    tgtcls: Optional[type[Any]] = None,
) -> None:

    tgtcls = tgtcls or mapcls
    if hasattr(tgtcls, "_proto_cls"):
        return

    # bind protobuf class constructor
    proto_cls = _get_class(mapcls, modules)
    setattr(tgtcls, "_proto_cls", proto_cls)

    fields = map_model_fields(mapcls)
    slot_names = tuple(f.name for f in fields)
    tgtcls.__slots__ = slot_names + ("_proto",)

    proto_kwargs: Dict[str, Callable[[Any], Any]] = {}

    for field in fields:
        # set slots getter and setter
        getter = make_getter(field)
        setter = make_setter(field)
        setattr(tgtcls, field.name, property(getter, setter))

        try:
            proto_kwargs[field.name] = make_kwarg(field)
        except TypeError:
            raise TypeError(
                f'Cannot resolve kwarg for class "{mapcls}", field "{field.name}"'
            )

    # set build proto kwargs
    setattr(
        tgtcls,
        "_build_proto_kwargs",
        lambda kwargs: {k: proto_kwargs[k](v) for k, v in kwargs.items()},
    )


def bind_proxy(
    mapcls: type[Any],
    modules: Dict[str, ModuleType],
) -> None:
    _bind_proxy(
        mapcls=mapcls, modules=modules, make_getter=make_getter, make_setter=make_setter
    )
