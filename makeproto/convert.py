from dataclasses import fields
from enum import Enum
from pathlib import Path
import sys
from types import ModuleType
from typing import Any,Optional, TypeVar, Union
import importlib.util

from makeproto.message import Message
from makeproto.prototypes import BaseMessage
# from google.protobuf.descriptor import FieldDescriptor

T = TypeVar("T")

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
            module_name = module_name.replace('_pb2','')
            modules[module_name] = module

    return modules

class Converter:

    def __init__(self, folder:Path) -> None:
        self._folder = folder
        self._modules:dict[str,Any] = import_py_files_from_folder(folder)

    def _get_class(self, module_name:str, cls_name:str)->type[Any]:
        mod = self._modules.get(module_name, None)
        if mod is None:
            raise KeyError(f'Module "{module_name}" does not exist.')
        clss = getattr(mod, cls_name)
        return clss

    def _resolve_convert_to(self,value:Union[Enum,BaseMessage, Any], type_:type[Any]):

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, BaseMessage):
            return self.to_proto(value)

        return value


    def to_proto(self, obj: BaseMessage, case_mode: Optional[str] = None) -> Any:

        args = {}

        needconvert:Optional[dict[str, tuple[type,type]]] = getattr(obj, "_needconvert", None)
        if needconvert is None:
            raise Exception(f'Need convert not defined for class: "{obj.__class__.__name__}"')

        for field in fields(obj):

            arg = field.name
            value = getattr(obj, arg)
            convert_tuple = needconvert.get(arg, None)
            if convert_tuple is not None:
                origin, type_ = convert_tuple
                if origin == object:
                    value = self._resolve_convert_to(value, type_)
                if origin in {list, set}:
                    value = [self._resolve_convert_to(v, type_) for v in value]
                    if origin is set:
                        value = set(value)
                elif origin is dict:
                    values_list = value.values()
                    values_list_converted = [self._resolve_convert_to(v, type_) for v in values_list]
                    value = dict(zip(value.keys(), values_list_converted))
            args[arg] = value

        obj_cls = type(obj)
        mod = obj_cls.__proto_file__
        cls_name = obj_cls.__name__
        proto_class = self._get_class(mod, cls_name)

        return proto_class(**args)


    def _resolve_convert_from(self, value:Union[int,type[BaseMessage], Any], type_:type[Any]):

        if isinstance(value, int):
            return type_(value)

        if issubclass(type_, BaseMessage):
            return self.from_proto(value, type_)

        return value

    def from_proto(self,obj: Any, clstype: type[BaseMessage]) -> Message:

        needconvert:Optional[dict[str, tuple[type,type]]] = getattr(clstype, "_needconvert", None)

        if needconvert is None:
            raise Exception(f'Need convert not defined for class: "{clstype.__name__}"')
        args = {}
        for field in obj.DESCRIPTOR.fields:
            name = field.name
            value = getattr(obj,name)

            convert_tuple = needconvert.get(name, None)
            if convert_tuple is not None:
                origin, type_ = convert_tuple

                if origin == object:
                    value = self._resolve_convert_from(value, type_)
                if origin in {list, set}:
                    value = [self._resolve_convert_from(v, type_) for v in value]
                    if origin is set:
                        value = set(value)
                elif origin is dict:
                    values_list = value.values()
                    values_list_converted = [self._resolve_convert_from(v, type_) for v in values_list]
                    value = dict(zip(value.keys(), values_list_converted))

            args[name] = value

        res = clstype(**args)

        return res

        # if field.type == FieldDescriptor.TYPE_MESSAGE:
        #     print(f"{name}: é uma mensagem (classe Protobuf) → {field.message_type.name}")
        # elif field.type == FieldDescriptor.TYPE_ENUM:
        #     print(f"{name}: é um enum {field.}")
        # else:
        #     print(f"{name}: é um tipo primitivo ")#({FieldDescriptor.Type.Name(field.type)})")
