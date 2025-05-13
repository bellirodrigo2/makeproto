import functools
import importlib.util
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any, Dict

from makeproto.mapclass import map_class_fields
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


def bind_init(cls: type[BaseMessage]) -> None:
    proto_cls = getattr(cls, "_proto_cls", None)
    if proto_cls is None:
        raise TypeError(f"No _proto_cls bound to class {cls.__name__}")

    fields = [f.name for f in map_class_fields(cls)]
    enums = getattr(cls, "_enums", {})
    nested_msgs = getattr(cls, "_nested_msgs", {})

    @functools.wraps(cls.__init__)
    def __init__(self: Any, **kwargs: Any) -> None:
        proto_kwargs = {}

        for k in fields:
            if k not in kwargs:
                continue
            value = kwargs[k]

            if k in enums:
                if isinstance(value, enums[k]):
                    value = value.value
                else:
                    raise TypeError(
                        f"Field '{k}' must be of type '{enums[k].__name__}'"
                    )

            elif k in nested_msgs:
                if isinstance(value, BaseMessage):
                    value = value._proto
                elif isinstance(value, nested_msgs[k]):
                    pass  # já é proto
                else:
                    raise TypeError(
                        f"Field '{k}' must be BaseMessage or {nested_msgs[k].__name__}, got {type(value).__name__}"
                    )

            proto_kwargs[k] = value
        self._proto = proto_cls(**proto_kwargs)

    cls.__init__ = __init__


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

    enums = {}
    nested_msgs = {}
    protofile = cls.protofile

    # get_class will raise if module or class not found
    proto_cls = get_class(protofile, cls.__name__)
    setattr(cls, "_proto_cls", proto_cls)  # protoclass bind

    args = map_class_fields(cls)
    for arg in args:
        bt = arg.basetype
        if isinstance(bt, type):
            if issubclass(bt, Enum):
                enums[arg.name] = bt
            elif issubclass(bt, BaseMessage):
                nested_protofile = bt.protofile
                nested_proto_cls = get_class(nested_protofile, bt.__name__)
                nested_msgs[arg.name] = nested_proto_cls
                bind_proxy(bt, modules)
    setattr(cls, "_enums", enums)
    setattr(cls, "_nested_msgs", nested_msgs)
    bind_init(cls)


class ProtoProxy:
    def __init__(self, proto_instance: Any, model_cls: type["BaseMessage"]):

        if not hasattr(model_cls, "_enums"):
            raise TypeError(f'Class "{model_cls.__name__}" has no "_enums" associated')
        if not hasattr(model_cls, "_nested_msgs"):
            raise TypeError(
                f'Class "{model_cls.__name__}" has no "_nested_msgs" associated'
            )

        self._proto = proto_instance
        self._model_cls = model_cls

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._proto, name)
        enum_ = getattr(self._model_cls, "_enums", {}).get(name, None)
        if enum_:
            return enum_(value)
        msg_ = getattr(self._model_cls, "_nested_msgs").get(name, None)
        if msg_:
            return ProtoProxy(value, msg_)
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"_enums", "_nested_msgs", "_proto", "_model_cls"}:
            super().__setattr__(name, value)
            return
        enum_ = getattr(self._model_cls, "_enums", {}).get(name, None)
        if enum_:
            value = value.value
        msg_ = getattr(self._model_cls, "_nested_msgs").get(name, None)
        if msg_:
            if isinstance(value, BaseMessage):
                value = value._proto  # type: ignore
            elif isinstance(value, msg_):
                pass  # it is proto class already
            else:
                raise TypeError(
                    f"Expected value of type BaseMessage or {msg_.__name__} for nested field '{name}', got {type(value).__name__}"
                )
        setattr(self._proto, name, value)
