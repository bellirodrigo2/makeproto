import importlib.util
from enum import Enum
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    ItemsView,
    Iterator,
    KeysView,
    List,
    MutableMapping,
    MutableSequence,
    Union,
    ValuesView,
)

from makeproto.mapclass import FuncArg, map_class_fields
from makeproto.prototypes import BaseProto


class Message(BaseProto):
    # _proto_cls: Optional[type[Any]] = None

    def __init__(self, _proto_proxy: Any = None, **kwargs: Any):
        if _proto_proxy:
            self._proto = _proto_proxy
        else:
            proto_class = getattr(self.__class__, "_proto_cls", None)
            if proto_class is None:
                raise TypeError(f'"_proto_cls" not set for "{self.__class__.__name__}"')
            self._proto = proto_class()
            for k, v in kwargs.items():
                setattr(self, k, v)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Message):
            return False
        return self._proto == other._proto

    def unwrap(self) -> Any:
        return self._proto

    def __repr__(self) -> str:
        fields = ", ".join(
            f"{k}={repr(getattr(self, k))}"
            for k in dir(self.__class__)
            if not k.startswith("_") and not callable(getattr(self.__class__, k))
        )
        return f"{self.__class__.__name__}({fields})"


class ListProxy(MutableSequence[Any]):
    def __init__(
        self,
        container: List[Any],
        get_v: Callable[[Any], Any],
        set_v: Callable[[Any], Any],
        base_type: type[Any],
    ) -> None:
        self._container = container
        self._get_v = get_v
        self._set_v = set_v
        self._base_type = base_type

    def __getitem__(self, i: Any) -> Any:
        return self._get_v(self._container[i])

    def __setitem__(self, i: Any, value: Any) -> None:
        try:
            self._container[i] = self._set_v(value)
        except TypeError:
            raise TypeError(
                f'At ListProxy set method for index: "{i}": Expected "{self._base_type.__name__}", found "{type(value).__name__}":{value}'
            )

    def __delitem__(self, index: Union[int, slice]) -> None:
        del self._container[index]

    def __iter__(self) -> Generator[Any, None, None]:
        return (self._get_v(v) for v in self._container)

    def __len__(self) -> int:
        return len(self._container)

    def __contains__(self, item: Any) -> bool:
        return any(self._get_v(v) == item for v in self._container)

    def append(self, value: Any) -> None:
        try:
            self._container.append(self._set_v(value))
        except TypeError:
            raise TypeError(
                f'At ListProxy append method: Expected "{self._base_type.__name__}", found "{type(value).__name__}":{value}'
            )

    def extend(self, values: Any) -> None:
        try:
            self._container.extend(self._set_v(v) for v in values)
        except TypeError:
            raise TypeError(
                f'At ListProxy extend method: Expected "List[{self._base_type.__name__}]", found "{type(values).__name__}":{values}'
            )

    def clear(self) -> None:
        del self._container[:]

    def insert(self, index: Any, value: Any) -> None:
        self._container.insert(index, self._set_v(value))

    def remove(self, value: Any) -> None:
        del self[self.index(value)]

    def pop(self, index: int = -1) -> Any:
        return self._get_v(self._container.pop(index))

    def index(self, value: Any, start: int = 0, stop: int = 9223372036854775807) -> int:
        for i in range(start, min(stop, len(self))):
            if self[i] == value:
                return i
        raise ValueError(f"{value!r} is not in list")

    def reverse(self) -> None:
        self._container.reverse()

    def sort(self) -> None:
        self._container.sort()

    def copy(self) -> List[Any]:
        return list(self)

    def __eq__(self, other: Any) -> bool:
        return list(self) == list(other)

    def __repr__(self) -> str:
        return repr(list(self))


def EnumListProxy(container: List[Any], enum_type: type[Enum]) -> ListProxy:
    return ListProxy(container, enum_type, lambda v: v.value, enum_type)


def MessageListProxy(container: List[Any], base_type: type[Message]) -> ListProxy:
    return ListProxy(container, base_type, lambda v: v.unwrap(), base_type)


def ValueListProxy(container: List[Any], base_type: type[Any]) -> ListProxy:
    return ListProxy(container, lambda v: v, lambda v: v, base_type)


DEFAULT_VALUE = object()


class DictProxy(MutableMapping[Any, Any]):
    def __init__(
        self,
        container: Dict[Any, Any],
        get_v: Callable[[Any], Any],
        set_v: Callable[[Any], Any],
        base_type: type[Any],
    ):
        self._container = container
        self._get_v = get_v
        self._set_v = set_v
        self._base_type = base_type

    def __getitem__(self, k: Any) -> Any:
        value = self._container.get(k, DEFAULT_VALUE)
        if value is DEFAULT_VALUE:
            return None
        return self._get_v(value)

    def get(self, k: Any, default: Any = None) -> Any:
        value = self._container.get(k, DEFAULT_VALUE)
        if value is DEFAULT_VALUE:
            return default
        return self._get_v(value)

    def set(self, k: Any, v: Any) -> None:
        self[k] = v

    def __setitem__(self, k: Any, v: Any) -> None:
        if v is None:
            raise TypeError(f'Can´t set "{k}" to None on DictProxy')
        try:
            if v is not None:
                self._container[k] = self._set_v(v)
        except (AttributeError, TypeError):
            raise TypeError(
                f'At DictProxy set method for key: "{k}": Expected "{self._base_type.__name__}", found "{type(v).__name__}":{v}'
            )

    def __contains__(self, k: Any) -> bool:
        return k in self._container

    def __delitem__(self, k: Any) -> None:
        del self._container[k]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._container)

    def keys(self) -> KeysView[Any]:
        return list(self._container.keys())

    def values(self) -> ValuesView[Any]:
        return [self._get_v(v) for v in self._container.values()]

    def items(self) -> ItemsView[Any, Any]:
        return [(k, self._get_v(v)) for k, v in self._container.items()]

    def update(self, d: Dict[Any, Any]) -> None:
        for k, v in d.items():
            self._container[k] = self._set_v(v)

    def clear(self) -> None:
        self._container.clear()

    def __eq__(self, other: Any) -> bool:
        return dict(self.items()) == dict(other)

    def __len__(self) -> int:
        return len(self._container)

    def __repr__(self) -> str:
        return repr(dict(self.items()))


def EnumDictProxy(container: Dict[Any, Any], enum_type: type[Enum]) -> DictProxy:
    return DictProxy(container, enum_type, lambda v: v.value, enum_type)


def MessageDictProxy(container: Dict[Any, Any], base_type: type[Message]) -> DictProxy:
    return DictProxy(container, base_type, lambda v: v.unwrap(), base_type)


def ValueDictProxy(container: Dict[Any, Any], base_type: type[Any]) -> DictProxy:
    return DictProxy(container, lambda v: v, lambda v: v, base_type)


def make_getter(field: FuncArg) -> Callable[[Any], Any]:
    name = field.name
    bt = field.basetype
    origin = field.origin
    args = field.args

    if origin is list:
        bt = args[0]
        if issubclass(bt, Enum):
            return lambda self: EnumListProxy(getattr(self._proto, name), bt)
        elif issubclass(bt, Message):
            return lambda self: MessageListProxy(getattr(self._proto, name), bt)
        else:
            return lambda self: ValueListProxy(getattr(self._proto, name), bt)

    elif origin is dict:
        bt = args[1]
        if issubclass(bt, Enum):
            return lambda self: EnumDictProxy(getattr(self._proto, name), bt)
        elif issubclass(bt, Message):
            return lambda self: MessageDictProxy(getattr(self._proto, name), bt)
        else:
            return lambda self: ValueDictProxy(getattr(self._proto, name), bt)

    elif origin is None:
        if issubclass(bt, Enum):
            return lambda self: bt(getattr(self._proto, name))
        elif issubclass(bt, Message):
            return lambda self: bt(getattr(self._proto, name))

    return lambda self: getattr(self._proto, name)


def make_setter(field: FuncArg) -> Callable[[Any, Any], None]:
    name = field.name
    bt = field.basetype
    origin = field.origin
    args = field.args

    def assign_value(self: Message, value: Any, set_v: Callable[[Any], Any]) -> None:
        try:
            setattr(self._proto, name, set_v(value))
        except (TypeError, AttributeError):
            raise TypeError(
                f'At class "{self.__class__.__name__}", field: "{name}" set: Expected "{bt.__name__}", found "{type(value).__name__}":{value}'
            )

    if origin is list:
        bt = args[0]

        def set_list(self: Any, value: Any, set_v: Callable[[Any], Any]) -> None:

            try:
                target = getattr(self._proto, name)
                target[:] = [set_v(v) for v in value]
            except (TypeError, AttributeError):
                raise TypeError(
                    f'At class "{self.__class__.__name__}", field: "{name}" set: Expected "List[{bt.__name__}]", found "{type(value).__name__}":{value}'
                )

        if issubclass(bt, Enum):
            return partial(set_list, set_v=lambda x: x.value)
        elif issubclass(bt, Message):
            return partial(set_list, set_v=lambda x: x.unwrap())
        else:
            return partial(set_list, set_v=lambda x: x)

    elif origin is dict:
        bt = args[1]

        def set_dict(
            self: Any, value: dict[Any, Any], set_v: Callable[[Any], Any]
        ) -> None:
            try:
                target = getattr(self._proto, name)
                target.clear()
                for k, v in value.items():
                    target[k] = set_v(v)
            except (TypeError, AttributeError):
                raise TypeError(
                    f'At class "{self.__class__.__name__}", field: "{name}" set: Expected "dict[{args[0].__name__},{bt.__name__}]", found "{type(value).__name__}": {value}'
                )

        if issubclass(bt, Enum):
            return partial(set_dict, set_v=lambda x: x.value)
        elif issubclass(bt, Message):
            return partial(set_dict, set_v=lambda x: x.unwrap())
        else:
            return partial(set_dict, set_v=lambda x: x)

    elif origin is None:
        if issubclass(bt, Enum):
            return partial(assign_value, set_v=lambda x: x.value)
        elif issubclass(bt, Message):
            return partial(assign_value, set_v=lambda x: x.unwrap())
    return partial(assign_value, set_v=lambda x: x)


def import_py_files_from_folder(folder: Path) -> dict[str, ModuleType]:
    modules: dict[str, ModuleType] = {}

    for py_file in folder.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        module_name = py_file.stem
        spec = importlib.util.spec_from_file_location(module_name, py_file)

        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # sys.modules[module_name] = module  # opcional
            spec.loader.exec_module(module)
            normalized_name = module_name.replace("_pb2", "")
            modules[normalized_name] = module

    return modules


def bind_proxy(
    mapcls: type[Any], modules: Dict[str, ModuleType], tgtcls: type[Message] = None
) -> None:
    def get_class(modname: str, clsname: str) -> type[Any]:
        mod = modules.get(modname, None)
        if mod is None:
            raise KeyError(f'Module "{modname}" does not exist.')
        clss = getattr(mod, clsname, None)
        if clss is None:
            raise KeyError(f'Module "{modname}" has no Class "{clsname}".')
        return clss

    tgtcls = tgtcls or mapcls

    if hasattr(tgtcls, "_proto_cls"):
        return  # already bound

    protofile = getattr(mapcls, "protofile", None)
    if protofile is None:
        raise KeyError(f'Class "{mapcls.__name__}" has no protofile() set')
    proto_cls = get_class(protofile(), mapcls.__name__)
    setattr(tgtcls, "_proto_cls", proto_cls)

    fields = map_class_fields(mapcls)
    slot_names = tuple(f.name for f in fields)

    tgtcls.__slots__ = slot_names + ("_proto",)

    for field in fields:
        getter = make_getter(field)
        setter = make_setter(field)
        setattr(tgtcls, field.name, property(getter, setter))
