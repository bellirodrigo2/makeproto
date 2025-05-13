import importlib.util
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict

from makeproto.mapclass import FuncArg, map_class_fields


class BaseMessage2:
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


def get_basemsg(value: Any, cls: type[BaseMessage2]) -> BaseMessage2:
    return cls(proto=value)


def set_basemsg(value: BaseMessage2) -> Any:
    return value.unwrap()


def get_enum_list(value: list[Any], enum_type: type[Enum]) -> list[Enum]:
    return [enum_type(v) for v in value]


def set_enum_list(value: list[Enum]) -> list[Any]:
    return [v.value for v in value]


def get_basemsg_list(value: list[Any], cls: type[BaseMessage2]) -> list[BaseMessage2]:
    return [cls(proto=v) for v in value]


def set_basemsg_list(value: list[BaseMessage2]) -> list[Any]:
    return [v.unwrap() for v in value]


def get_enum_dict(value: dict[Any, Any], enum_type: type[Enum]) -> dict[Any, Enum]:
    return {k: enum_type(v) for k, v in value.items()}


def set_enum_dict(value: dict[Any, Enum]) -> dict[Any, Any]:
    return {k: v.value for k, v in value.items()}


def get_basemsg_dict(
    value: dict[Any, Any], cls: type[BaseMessage2]
) -> dict[Any, BaseMessage2]:
    return {k: cls(proto=v) for k, v in value.items()}


def set_basemsg_dict(value: dict[Any, BaseMessage2]) -> dict[Any, Any]:
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
        elif issubclass(bt, BaseMessage2):
            return lambda self: get_basemsg_list(getattr(self._proto, name), bt)

    elif origin is dict:
        bt = args[1]
        if issubclass(bt, Enum):
            return lambda self: get_enum_dict(getattr(self._proto, name), bt)
        elif issubclass(bt, BaseMessage2):
            return lambda self: get_basemsg_dict(getattr(self._proto, name), bt)

    elif origin is None:
        if issubclass(bt, Enum):
            return lambda self: get_enum(getattr(self._proto, name), bt)
        elif issubclass(bt, BaseMessage2):
            return lambda self: get_basemsg(getattr(self._proto, name), bt)

    return lambda self: getattr(self._proto, name)


def make_setter(field: FuncArg) -> Callable[[Any, Any], None]:
    name = field.name
    bt = field.basetype
    origin = field.origin
    args = field.args

    if origin is list:
        bt = args[0]
        if issubclass(bt, Enum):
            return lambda self, value: setattr(self._proto, name, set_enum_list(value))
        elif issubclass(bt, BaseMessage2):
            return lambda self, value: setattr(
                self._proto, name, set_basemsg_list(value)
            )

    elif origin is dict:
        bt = args[1]
        if issubclass(bt, Enum):
            return lambda self, value: setattr(self._proto, name, set_enum_dict(value))
        elif issubclass(bt, BaseMessage2):
            return lambda self, value: setattr(
                self._proto, name, set_basemsg_dict(value)
            )

    elif origin is None:
        if issubclass(bt, Enum):
            return lambda self, value: setattr(self._proto, name, set_enum(value))
        elif issubclass(bt, BaseMessage2):
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


def bind_proxy2(cls: type[BaseMessage2], modules: Dict[str, ModuleType]) -> None:
    def get_class(modname: str, clsname: str) -> type[Any]:
        mod = modules.get(modname, None)
        if mod is None:
            raise KeyError(f'Module "{modname}" does not exist.')
        clss = getattr(mod, clsname, None)
        if clss is None:
            raise KeyError(f'Module "{modname}" has no Class "{clsname}".')
        return clss

    if not isinstance(cls, type) or not issubclass(cls, BaseMessage2):  # type: ignore
        raise ValueError(
            f"Class '{cls.__name__}' is not subclass of BaseMessage2. Found '{cls}'"
        )

    if hasattr(cls, "_proto_cls"):
        return  # already bound

    protofile = cls.protofile
    proto_cls = get_class(protofile, cls.__name__)
    setattr(cls, "_proto_cls", proto_cls)

    fields = map_class_fields(cls)
    slot_names = tuple(f.name for f in fields)

    cls.__slots__ = slot_names + ("_proto",)

    for field in fields:
        getter = make_getter(field)
        setter = make_setter(field)
        setattr(cls, field.name, property(getter, setter))
