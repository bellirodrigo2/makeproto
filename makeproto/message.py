from collections import defaultdict
from typing import Any, Optional

from makeproto.mapclass import map_class_fields
from makeproto.prototypes import BaseMessage, OneOf


def define_oneof_fields(cls: type[BaseMessage]) -> None:
    args = map_class_fields(cls)
    oneof: dict[str, set[str]] = defaultdict(set)

    for arg in args:
        instance = arg.getinstance(OneOf)
        if instance is not None:
            key = instance.key
            oneof[key].add(arg.name)
    setattr(cls, "_oneof", oneof)


class Message(BaseMessage):

    _oneof: dict[str, set[str]]
    _selected: dict[str, str]

    def __new__(cls: type[Any], *args: Any, **kwargs: Any) -> Any:
        self = super().__new__(cls)
        object.__setattr__(self, "_selected", {})
        return self

    def _get_oneof_group(self, name: str) -> Optional[tuple[str, set[str]]]:
        for k, v in self._oneof.items():
            if name in v:
                return k, v
        return None

    def _clear_group(self, name: str) -> None:
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
