from types import ModuleType
from typing import Any, Dict

from makeproto.proxy.binder import _bind_proxy
from makeproto.proxy.proto_get_set import make_getter, make_kwarg, make_setter


def bind_proxy(
    mapcls: type[Any],
    modules: Dict[str, ModuleType],
) -> None:
    _bind_proxy(
        mapcls=mapcls,
        modules=modules,
        make_getter=make_getter,
        make_setter=make_setter,
        make_kwarg=make_kwarg,
    )
