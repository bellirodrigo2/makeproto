from enum import Enum
from functools import partial
from typing import Any, Callable

from makeproto.mapclass import FuncArg
from makeproto.proxy.proxy import (
    EnumDictProxy,
    EnumListProxy,
    MessageDictProxy,
    MessageListProxy,
    ProxyMessage,
    ValueDictProxy,
    ValueListProxy,
)

# ----------------- GETTERS -------------------------------------------------


def list_getter_factory(bt: type[Any], name: str) -> Callable[[Any], Any]:
    if issubclass(bt, Enum):
        return lambda self: EnumListProxy(getattr(self._wrapped, name), bt)
    elif issubclass(bt, ProxyMessage):
        return lambda self: MessageListProxy(getattr(self._wrapped, name), bt)
    else:
        return lambda self: ValueListProxy(getattr(self._wrapped, name), bt)


def dict_getter_factory(bt: type[Any], name: str) -> Callable[[Any], Any]:
    if issubclass(bt, Enum):
        return lambda self: EnumDictProxy(getattr(self._wrapped, name), bt)
    elif issubclass(bt, ProxyMessage):
        return lambda self: MessageDictProxy(getattr(self._wrapped, name), bt)
    else:
        return lambda self: ValueDictProxy(getattr(self._wrapped, name), bt)


def single_getter_factory(bt: type[Any], name: str) -> Callable[[Any], Any]:
    if issubclass(bt, Enum):
        return lambda self: bt(getattr(self._wrapped, name))
    elif issubclass(bt, ProxyMessage):
        return lambda self: bt(getattr(self._wrapped, name))
    else:
        return lambda self: getattr(self._wrapped, name)


def make_getter(field: FuncArg) -> Callable[[Any], Any]:
    name = field.name
    bt = field.basetype
    origin = field.origin
    args = field.args

    if origin is list:
        bt = args[0]
        return list_getter_factory(bt, name)

    elif origin is dict:
        bt = args[1]
        return dict_getter_factory(bt, name)

    elif origin is None:
        return single_getter_factory(bt, name)
    raise TypeError(f'Can´t resolve getter for field: "{name}"')


# ----------------- SETTERS -------------------------------------------------


def list_setter_factory(bt: type[Any], name: str) -> Callable[[Any, Any], Any]:

    def set_list(self: Any, value: Any, set_v: Callable[[Any], Any]) -> None:

        try:
            target = getattr(self._wrapped, name)
            target[:] = [set_v(v) for v in value]
        except (TypeError, AttributeError) as e:
            raise TypeError(
                f'At class "{self.__class__.__name__}", field: "{name}" set: Expected "List[{bt.__name__}]", found "{type(value).__name__}":{value}'
            ) from e

    # def set_list_message(self: Message, value: Any) -> None:
    #     try:
    #         target = getattr(self._wrapped, name)
    #         del target[:]
    #         for item in value:
    #             target.add().CopyFrom(item.unwrap)
    #     except Exception as e:
    #         raise TypeError(
    #             f'At class "{self.__class__.__name__}", field: "{name}" list[ProxyMessage] set failed: {value}'
    #         ) from e

    if issubclass(bt, Enum):
        return partial(set_list, set_v=lambda x: x.value)
    elif issubclass(bt, ProxyMessage):
        return partial(set_list, set_v=lambda x: x.unwrap)
    else:
        return partial(set_list, set_v=lambda x: x)


def dict_setter_factory(
    bt: type[Any], dict_key: str, name: str
) -> Callable[[Any, Any], Any]:

    def set_dict(self: Any, value: dict[Any, Any], set_v: Callable[[Any], Any]) -> None:
        try:
            target = getattr(self._wrapped, name)
            target.clear()
            for k, v in value.items():
                target[k] = set_v(v)
        except (TypeError, AttributeError) as e:
            raise TypeError(
                f'At class "{self.__class__.__name__}", field: "{name}" set: Expected "dict[{dict_key},{bt.__name__}]", found "{type(value).__name__}": {value}'
            ) from e

    # def set_dict_message(self: Message, value: Any) -> None:
    #     try:
    #         target = getattr(self._wrapped, name)
    #         target.clear()
    #         for k, v in value.items():
    #             target[k].CopyFrom(v.unwrap)
    #     except Exception as e:
    #         raise TypeError(
    #             f'At class "{self.__class__.__name__}", field: "{name}" dict[ProxyMessage] set failed: {value}'
    #         ) from e

    if issubclass(bt, Enum):
        return partial(set_dict, set_v=lambda x: x.value)
    elif issubclass(bt, ProxyMessage):
        return partial(set_dict, set_v=lambda x: x.unwrap)
    else:
        return partial(set_dict, set_v=lambda x: x)


def single_setter_factory(bt: type[Any], name: str) -> Callable[[Any, Any], Any]:
    def assign_value(
        self: ProxyMessage, value: Any, set_v: Callable[[Any], Any]
    ) -> None:
        try:
            setattr(self.unwrap, name, set_v(value))
        except (TypeError, AttributeError) as e:
            raise TypeError(
                f'At class "{self.__class__.__name__}", field: "{name}" set: Expected "{bt.__name__}", found "{type(value).__name__}":{value}'
            ) from e

    def assign_message(self: ProxyMessage, value: Any) -> None:
        try:
            target = getattr(self.unwrap, name)
            print("aqui")
            target.CopyFrom(value.unwrap)
        except (TypeError, AttributeError) as e:
            raise TypeError(
                f'At class "{self.__class__.__name__}", field: "{name}" set: Expected "{bt.__name__}", found "{type(value).__name__}":{value}'
            ) from e

    if issubclass(bt, Enum):
        return partial(assign_value, set_v=lambda x: x.value)
    elif issubclass(bt, ProxyMessage):
        return assign_message
    else:
        return partial(assign_value, set_v=lambda x: x)


def make_setter(field: FuncArg) -> Callable[[Any, Any], Any]:
    name = field.name
    bt = field.basetype
    origin = field.origin
    args = field.args

    if origin is list:
        bt = args[0]
        return list_setter_factory(bt, name)

    elif origin is dict:
        bt = args[1]
        return dict_setter_factory(bt, args[0].__name__, name)

    elif origin is None:
        return single_setter_factory(bt, name)
    raise TypeError(f'Can´t resolve setter for field: "{name}"')


# ----------------- KWARGS ------------------------------------------------


def single_kwarg_factory(bt: type[Any]) -> Callable[[Any], Any]:
    if issubclass(bt, Enum):
        return lambda v: v.value
    elif issubclass(bt, ProxyMessage):
        return lambda v: v.unwrap
    else:
        return lambda v: v


def list_kwarg_factory(bt: type[Any]) -> Callable[[Any], Any]:
    if issubclass(bt, Enum):
        return lambda value: [v.value for v in value]
    elif issubclass(bt, ProxyMessage):
        return lambda value: [v.unwrap for v in value]
    else:
        return lambda value: value


def dict_kwarg_factory(bt: type[Any]) -> Callable[[Any], Any]:
    if issubclass(bt, Enum):
        return lambda value: {k: v.value for k, v in value.items()}
    elif issubclass(bt, ProxyMessage):
        return lambda value: {k: v.unwrap for k, v in value.items()}
    else:
        return lambda value: value


def make_kwarg(field: FuncArg) -> Callable[[Any], Any]:
    """
    Transform a dict of Python values (Message, Enum, list, dict)
    to viable args for protobuf constructor.
    """
    bt = field.basetype
    origin = field.origin
    args = field.args

    if origin is list:
        bt = args[0]
        return list_kwarg_factory(bt)

    elif origin is dict:
        bt = args[1]
        return dict_kwarg_factory(bt)

    elif origin is None:
        return single_kwarg_factory(bt)
    raise TypeError
