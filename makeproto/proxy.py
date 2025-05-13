import functools
import importlib.util
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict

from makeproto.mapclass import FuncArg, map_class_fields
from makeproto.prototypes import BaseMessage


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


class ProtoProxy:
    def __init__(self, proto_instance: Any) -> None:
        self._proto = proto_instance

    def unwrap(self: Any) -> Any:
        return self._proto


def bind_proxy(cls: type[BaseMessage], modules: Dict[str, ModuleType]) -> None:
    def get_class(modname: str, clsname: str) -> type[Any]:
        mod = modules.get(modname, None)
        if mod is None:
            raise KeyError(f'Module "{modname}" does not exist.')
        clss = getattr(mod, clsname, None)
        if clss is None:
            raise KeyError(f'Module "{modname}" has no Class "{clsname}".')
        return clss

    if not isinstance(cls, type) or not issubclass(cls, BaseMessage):  # type: ignore
        raise ValueError(
            f"Class '{cls.__name__}' is not subclass of BaseMessage. Found '{cls}'"
        )

    if hasattr(cls, "_proto_cls"):
        return  # already bound

    protofile = cls.protofile

    proto_cls = get_class(protofile, cls.__name__)
    setattr(cls, "_proto_cls", proto_cls)  # protoclass bind


def to_proto(msg: BaseMessage) -> Any:
    proto_cls = getattr(msg.__class__, "_proxy_cls", None)
    if proto_cls is None:
        raise TypeError(f"No _proto_cls bound to class {cls.__name__}")

    fields = [f.name for f in map_class_fields(cls)]

    proto_instance = proto_cls()
    proxy = ProtoProxy(proto_instance)
    for k in fields:
        ...
        # PRECISA SER RECURSIVO
    #     if k in kwargs:
    #         setattr(proxy, k, kwargs[k])


def bind_init(cls: type[BaseMessage]) -> None:
    proto_cls = getattr(cls, "_proto_cls", None)
    if proto_cls is None:
        raise TypeError(f"No _proto_cls bound to class {cls.__name__}")

    fields = [f.name for f in map_class_fields(cls)]

    @functools.wraps(cls.__init__)
    def __init__(self: Any, **kwargs: Any) -> None:
        proto_instance = proto_cls()
        self._proto = proto_instance
        proxy = ProtoProxy(proto_instance)

        for k in fields:
            if k in kwargs:
                setattr(proxy, k, kwargs[k])
        self._proxy = proxy

    def unwrap(self: Any) -> Any:
        return self._proto

    # Attach both __init__ and unwrap methods to the class
    cls.__init__ = __init__
    setattr(cls, "unwrap", unwrap)


def get_enum(value: Any, enum_type: type[Enum]) -> Enum:
    return enum_type(value)


def set_enum(value: Enum) -> Any:
    return value.value


def get_basemsg(value: Any, proxy: type[ProtoProxy]) -> BaseMessage:
    return proxy(value)


def set_basemsg(value: BaseMessage) -> Any:
    return value.unwrap()


def set_enum_list(value: list[Enum]) -> list[Any]:
    return [v.value for v in value]


def get_enum_list(value: Any, enum_type: type[Enum]) -> list[Enum]:
    return [enum_type(v) for v in value]


def set_basemsg_list(value: list[BaseMessage]) -> list[Any]:
    return [v.unwrap() for v in value]


def get_basemsg_list(value: Any, proxy: type[ProtoProxy]) -> list[BaseMessage]:
    return [proxy(v) for v in value]


def set_enum_dict(value: dict[Any, Enum]) -> dict[Any, Any]:
    return {k: v.value for k, v in value.items()}


def get_enum_dict(value: Any, enum_type: type[Enum]) -> dict[Any, Enum]:
    return {k: enum_type(v) for k, v in value.items()}


def get_basemsg_dict(value: dict[Any, BaseMessage]) -> dict[Any, Any]:
    return {k: v.unwrap() for k, v in value.items()}


def set_basemsg_dict(value: Any, proxy: type[ProtoProxy]) -> dict[Any, BaseMessage]:
    return {k: proxy(v) for k, v in value.items()}


def make_getter(field: FuncArg) -> Callable[[Any], Any]:
    name = field.name
    bt = field.basetype

    origin = field.origin
    args = field.args

    if origin is list:
        bt = args[0]
        if issubclass(bt, Enum):
            enum_type = bt
            return lambda self: get_enum_list(getattr(self._proto, name), enum_type)
        elif issubclass(bt, BaseMessage):
            proxy_ = getattr(bt, "_proxy_cls", None) or make_proxy_class(bt)
            return lambda self: get_basemsg_list(getattr(self._proto, name), proxy_)

    elif origin is dict:
        bt = args[1]
        if issubclass(bt, Enum):
            enum_type = bt
            return lambda self: get_enum_dict(getattr(self._proto, name), enum_type)
        elif issubclass(bt, BaseMessage):
            proxy_ = getattr(bt, "_proxy_cls", None) or make_proxy_class(bt)
            return lambda self: get_basemsg_dict(getattr(self._proto, name))

    elif origin is None:
        if issubclass(bt, Enum):
            enum_type = bt
            return lambda self: get_enum(getattr(self._proto, name), enum_type)

        elif issubclass(bt, BaseMessage):
            proxy_ = getattr(bt, "_proxy_cls", None) or make_proxy_class(bt)
            return lambda self: get_basemsg(getattr(self._proto, name), proxy_)

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
        elif issubclass(bt, BaseMessage):
            return lambda self, value: setattr(
                self._proto, name, set_basemsg_list(value)
            )

    elif origin is dict:
        bt = args[1]
        if issubclass(bt, Enum):
            return lambda self, value: setattr(self._proto, name, set_enum_dict(value))
        elif issubclass(bt, BaseMessage):
            proxy_ = getattr(bt, "_proxy_cls", None) or make_proxy_class(bt)
            return lambda self, value: setattr(
                self._proto, name, set_basemsg_dict(value, proxy_)
            )

    elif origin is None:
        if issubclass(bt, Enum):
            return lambda self, value: setattr(self._proto, name, set_enum(value))
        elif issubclass(bt, BaseMessage):
            return lambda self, value: setattr(self._proto, name, set_basemsg(value))

    return lambda self, value: setattr(self._proto, name, value)


def make_proxy_class(model_cls: type[BaseMessage]) -> type[ProtoProxy]:

    fields = map_class_fields(model_cls)
    slots = [f.name for f in fields] + ["_proto"]
    namespace = {"__slots__": slots}

    # Bind one getter/setter per field
    for field in fields:
        get_fn = make_getter(field)
        set_fn = make_setter(field)
        namespace[field.name] = property(get_fn, set_fn)

    proxy_cls = type(f"{model_cls.__name__}Proxy", (ProtoProxy,), namespace)

    # Bind a reference to the generated proxy class back to the BaseMessage
    if not hasattr(model_cls, "_proxy_cls"):
        setattr(model_cls, "_proxy_cls", proxy_cls)

    return proxy_cls
