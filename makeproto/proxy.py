import importlib.util
from enum import Enum
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Any

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
            module_name = module_name.replace("_pb2", "")
            modules[module_name] = module

    return modules


class ProxyProvider:

    def __init__(self, folder: Path) -> None:
        self._folder = folder
        self._modules: dict[str, Any] = import_py_files_from_folder(folder)

    def _get_class(self, module_name: str, cls_name: str) -> type[Any]:
        mod = self._modules.get(module_name, None)
        if mod is None:
            raise KeyError(f'Module "{module_name}" does not exist.')
        clss = getattr(mod, cls_name)
        return clss

    def define_proxy_fields(self, cls: type[BaseMessage]) -> None:
        args = map_class_fields(cls)
        enums = {}
        nested_msgs = {}

        protofile = getattr(cls, "protofile", None)
        if not protofile:
            raise ValueError(f"{cls.__name__} is missing protofile attribute")

        proto_cls = self._get_class(protofile, cls.__name__)
        setattr(cls, "_proto_cls", proto_cls)  # bind principal (raiz)

        for arg in args:
            if isinstance(arg.basetype, type):
                if issubclass(arg.basetype, Enum):
                    enums[arg.name] = arg.basetype
                elif issubclass(arg.basetype, BaseMessage):
                    # Bind nested message
                    nested_proto_cls = self._get_class(protofile, arg.basetype.__name__)
                    nested_msgs[arg.name] = nested_proto_cls
                    setattr(
                        arg.basetype, "_proto_cls", nested_proto_cls
                    )  # opcional, se quiser aninhar

        setattr(cls, "_enums", enums)
        setattr(cls, "_nested_msgs", nested_msgs)


class ProtoProxy:
    def __init__(self, proto_instance: Any, model_cls: type["BaseMessage"]):
        self._proto = proto_instance
        self._model_cls = model_cls

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._proto, name)
        enum_ = self._enums.get(name)
        return enum_(value) if enum_ else value

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_enums":
            super().__setattr__(name, value)
            return
        enum_ = getattr(self._model_cls, "_enums", {}).get(name)
        if enum_:
            value = value.value
        setattr(self._proto, name, value)
