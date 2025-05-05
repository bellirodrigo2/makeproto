from dataclasses import dataclass, field
from typing import Any, Optional

from makeproto.makemsg import get_oneof_details
from makeproto.mapclass import get_dataclass_fields
from makeproto.prototypes import BaseMessage


@dataclass
class OneOfObj:
    selected: str
    args: set[str]


@dataclass
class Message(BaseMessage):

    _oneof: dict[str, OneOfObj] = field(init=False)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(
            cls,
        )
        object.__setattr__(instance, "_oneof", {})
        return instance

    def __post_init__(self):

        args = get_dataclass_fields(self.__class__)

        for arg in args:

            oodetails = get_oneof_details(arg)
            if oodetails:
                key, fname, _ = oodetails
                if key not in self._oneof:
                    self._oneof[key] = OneOfObj(selected="", args=set([fname]))
                else:
                    self._oneof[key].args.add(fname)
                val = getattr(self, fname)
                if val is not None:
                    if self._oneof[key].selected:
                        raise ValueError(
                            f'More than one OneOf field set for OneOf: "{key}"'
                        )
                    self._oneof[key].selected = fname

    def _get_oneof_group(self, name: str):
        for v in self._oneof.values():
            if name in v.args:
                return v
        return None

    def _clear_group(self, name: str):
        group = self._get_oneof_group(name)
        if group is not None:
            for arg in group.args:
                object.__setattr__(self, arg, None)
            group.selected = name

    def __setattr__(self, name: str, value: Any) -> None:
        self._clear_group(name)

        return super().__setattr__(name, value)

    def WhichOneof(self, key: str) -> Optional[str]:
        if key not in self._oneof:
            return None
        return self._oneof[key].selected
