import importlib.util
from enum import Enum
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict

from makeproto.mapclass import FuncArg, map_class_fields
from makeproto.prototypes import BaseProto


class Message(BaseProto):
    def __init__(self, proto: Any = None, **kwargs: Any):
        if proto:
            self._proto = proto
        else:
            proto_class = getattr(self.__class__, "_proto_cls", None)
            if proto_class is None:
                raise TypeError
            self._proto = proto_class()
            for k, v in kwargs.items():
                setattr(self, k, v)

    def unwrap(self) -> Any:
        return self._proto


def get_enum(value: Any, enum_type: type[Enum]) -> Enum:
    return enum_type(value)


def set_enum(value: Enum) -> Any:
    return value.value


def get_basemsg(value: Any, cls: type[Message]) -> Message:
    return cls(proto=value)


def set_basemsg(value: Message) -> Any:
    return value.unwrap()


def get_enum_list(value: list[Any], enum_type: type[Enum]) -> list[Enum]:
    return [enum_type(v) for v in value]


def get_basemsg_list(value: list[Any], cls: type[Message]) -> list[Message]:
    return [cls(proto=v) for v in value]


def get_enum_dict(value: dict[Any, Any], enum_type: type[Enum]) -> dict[Any, Enum]:
    return {k: enum_type(v) for k, v in value.items()}


def set_enum_dict(value: dict[Any, Enum]) -> dict[Any, Any]:
    return {k: v.value for k, v in value.items()}


def get_basemsg_dict(value: dict[Any, Any], cls: type[Message]) -> dict[Any, Message]:
    return {k: cls(proto=v) for k, v in value.items()}


def set_basemsg_dict(value: dict[Any, Message]) -> dict[Any, Any]:
    return {k: v.unwrap() for k, v in value.items()}


def make_getter(field: FuncArg) -> Callable[[Any], Any]:
    name = field.name
    bt = field.basetype
    origin = field.origin
    args = field.args

    if origin is list:
        bt = args[0]
        if issubclass(bt, Enum):
            return lambda self: get_enum_list(getattr(self._proto, name), bt)
        elif issubclass(bt, Message):
            return lambda self: get_basemsg_list(getattr(self._proto, name), bt)

    elif origin is dict:
        bt = args[1]
        if issubclass(bt, Enum):
            return lambda self: get_enum_dict(getattr(self._proto, name), bt)
        elif issubclass(bt, Message):
            return lambda self: get_basemsg_dict(getattr(self._proto, name), bt)

    elif origin is None:
        if issubclass(bt, Enum):
            return lambda self: get_enum(getattr(self._proto, name), bt)
        elif issubclass(bt, Message):
            return lambda self: get_basemsg(getattr(self._proto, name), bt)

    return lambda self: getattr(self._proto, name)


def make_setter(field: FuncArg) -> Callable[[Any, Any], None]:
    name = field.name
    bt = field.basetype
    origin = field.origin
    args = field.args

    if origin is list:
        bt = args[0]

        def set_list(self: Any, value: Any, set_v: Callable[[Any], Any]) -> None:
            target = getattr(self._proto, name)
            target[:] = [set_v(v) for v in value]

        if issubclass(bt, Enum):
            return partial(set_list, set_v=set_enum)
        elif issubclass(bt, Message):
            return partial(set_list, set_v=set_basemsg)
        else:
            return partial(set_list, set_v=lambda x: x)

    elif origin is dict:
        bt = args[1]

        def set_dict(
            self: Any, value: dict[Any, Any], set_v: Callable[[Any], Any]
        ) -> None:
            target = getattr(self._proto, name)
            target.clear()
            for k, v in value.items():
                target[k] = set_v(v)

        if issubclass(bt, Enum):
            return partial(set_dict, set_v=set_enum)
        elif issubclass(bt, Message):
            return partial(set_dict, set_v=set_basemsg)
        else:
            return partial(set_dict, set_v=lambda x: x)

    elif origin is None:
        if issubclass(bt, Enum):
            return lambda self, value: setattr(self._proto, name, set_enum(value))
        elif issubclass(bt, Message):
            return lambda self, value: setattr(self._proto, name, set_basemsg(value))

    return lambda self, value: setattr(self._proto, name, value)


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

    protofile = mapcls.protofile()
    proto_cls = get_class(protofile, mapcls.__name__)
    setattr(tgtcls, "_proto_cls", proto_cls)

    fields = map_class_fields(mapcls)
    slot_names = tuple(f.name for f in fields)

    tgtcls.__slots__ = slot_names + ("_proto",)

    for field in fields:
        getter = make_getter(field)
        setter = make_setter(field)
        setattr(tgtcls, field.name, property(getter, setter))
