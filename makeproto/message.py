from collections import defaultdict
from enum import Enum
from typing import Any, Mapping, Optional

from makeproto.makemsg import get_oneof_details
from makeproto.mapclass import get_dataclass_fields
from makeproto.prototypes import BaseMessage


def define_oneof_fields(cls:type[BaseMessage]):
    args = get_dataclass_fields(cls)
    oneof: dict[str, set[str]] = defaultdict(set)
    for arg in args:
        oodetails = get_oneof_details(arg)
        if oodetails:
            key, fname, _ = oodetails
            oneof[key].add(fname)
    setattr(cls,'_oneof', oneof)

def enum_name_factory(enum_cls: type[Enum], value: int) -> str:
    try:
        return enum_cls(value).name
    except ValueError:
        raise ValueError(f"{value} is not a valid value for {enum_cls.__name__}")

def define_enums_fields(cls:type[BaseMessage]) -> Mapping[str, type[Enum]]:
    args = get_dataclass_fields(cls)

    enums:dict[str,type[Enum]] = {}
    for arg in args:
        if arg.basetype and arg.istype(Enum):
            enums[arg.name] = arg.basetype
    setattr(cls,'_enums_map', enums)

class Message(BaseMessage):

    def __new__(cls: type[Any], *args:Any, **kwargs:Any) -> Any:
        self = super().__new__(cls)
        object.__setattr__(self, '_selected', {})
        return self

    def _get_oneof_group(self, name: str):
        for k,v in self._oneof.items():
            if name in v:
                return k,v
        return None

    def _clear_group(self, name: str):
        getgroup = self._get_oneof_group(name)
        if getgroup is not None:
            key, group = getgroup
            for arg in group:
                if arg == name:
                    continue
                object.__setattr__(self, arg, None)
            self._selected[key] = name

    def __setattr__(self, name: str, value: Any) -> None:
        if not name.startswith("_") and value is not None:
            self._clear_group(name)
        return super().__setattr__(name, value)

    def WhichOneof(self, key: str) -> Optional[str]:
        return self._selected.get(key, None)