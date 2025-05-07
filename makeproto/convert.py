import importlib.util
from dataclasses import fields
from enum import Enum
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable, Optional, TypeVar

from makeproto.mapclass import get_dataclass_fields
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
            module_name = module_name.replace("_pb2", "")
            modules[module_name] = module

    return modules


class ConvertingError(Exception):

    def __init__(
        self,
        converting: str,
        clstype: str,
        field: str,
        value: Any,
        expected: str,
        cause: Exception,
    ):

        self.msg = f'Error when converting "{clstype}" {converting} proto. Field "{field}" has value "{value}" of type "{type(value)}", when "{expected}" was expected'
        self.__cause__ = cause
        super().__init__(self.msg)


class Converter:

    def __init__(self, folder: Path) -> None:
        self._folder = folder
        self._modules: dict[str, Any] = import_py_files_from_folder(folder)

    def _get_class(self, module_name: str, cls_name: str) -> type[Any]:
        mod = self._modules.get(module_name, None)
        if mod is None:
            raise KeyError(f'Module "{module_name}" does not exist.')
        clss = getattr(mod, cls_name)
        return clss

    def to_proto(self, obj: BaseMessage, case_mode: Optional[str] = None) -> Any:

        args = {}

        needconvert: Optional[dict[str, Converter.ConvertResolver]] = getattr(
            obj, "_needconvert", None
        )
        if needconvert is None:
            raise Exception(
                f'Need convert not defined for class: "{obj.__class__.__name__}"'
            )

        try:
            arg = "None"
            expected = "None"
            value = None
            for field in fields(obj):

                arg = field.name
                value = getattr(obj, arg)
                convert_resolver = needconvert.get(arg, None)
                if convert_resolver is not None:
                    expected = convert_resolver.expected_to_proto
                    convertedvalue = convert_resolver.to_proto(value)
                    value = convertedvalue
                args[arg] = value
        except Exception as e:
            err = ConvertingError(
                converting="to",
                clstype=type(obj).__name__,
                field=arg,
                value=value,
                expected=expected,
                cause=e,
            )
            raise err

        obj_cls = type(obj)
        mod = obj_cls.__proto_file__
        cls_name = obj_cls.__name__
        proto_class = self._get_class(mod, cls_name)

        return proto_class(**args)

    def from_proto(self, obj: Any, clstype: type[BaseMessage]) -> Message:

        needconvert: Optional[dict[str, Converter.ConvertResolver]] = getattr(
            clstype, "_needconvert", None
        )

        if needconvert is None:
            raise Exception(f'Need convert not defined for class: "{clstype.__name__}"')
        args = {}
        for field in obj.DESCRIPTOR.fields:
            name = field.name
            value = getattr(obj, name)

            convert_resolver = needconvert.get(name, None)
            if convert_resolver is not None:
                value = convert_resolver.from_proto(value)
            args[name] = value

        res = clstype(**args)

        return res

    class ConvertResolver:

        def __init__(
            self,
            from_proto: Callable[[Any], Any],
            to_proto: Callable[[Any], Any],
            expected_to_proto: str,
        ):
            self.from_proto = from_proto
            self.to_proto = to_proto
            self.expected_to_proto = expected_to_proto

    def _resolve_single_enum_from(self, value: Any, type_b: type[Enum]):
        # if not isinstance(value, int):
        # raise ValueError(f'Resolve Single Enum from should get an "int" as value, but got {type(value)}')
        return type_b(value)

    def _resolve_single_enum_to(self, value: Any):
        # if isinstance(value, Enum):
        # raise ValueError(f'Resolve Single Enum to should get an "Enum" as value, but got {type(value)}')
        return value.value

    def _resolve_single_basemessage_from(self, value: Any, type_b: type[BaseMessage]):
        return self.from_proto(value, type_b)

    def _resolve_single_basemessage_to(self, value: Any):
        return self.to_proto(value)

    def _resolve_list_enum_to(self, value: Any):
        return [v.value for v in value]

    def _resolve_list_enum_from(self, value: Any, type_b: type[Enum]):
        return [type_b(v) for v in value]

    def _resolve_list_basemessage_to(self, value: Any):
        return [self.to_proto(v) for v in value]

    def _resolve_list_basemessage_from(self, value: Any, type_b: type[BaseMessage]):
        return [self.from_proto(v, type_b) for v in value]

    def _resolve_dict_enum_to(self, value: Any):
        keys = value.keys()
        values = value.values()

        resolved_values = [v.value for v in values]

        return dict(zip(keys, resolved_values))

    def _resolve_dict_enum_from(self, value: Any, type_b: type[Enum]):
        keys = value.keys()
        values = value.values()

        resolved_values = [type_b(v) for v in values]

        return dict(zip(keys, resolved_values))

    def _resolve_dict_basemessage_to(self, value: Any):
        keys = value.keys()
        values = value.values()

        resolved_values = [self.to_proto(v) for v in values]

        return dict(zip(keys, resolved_values))

    def _resolve_dict_basemessage_from(self, value: Any, type_b: type[BaseMessage]):
        keys = value.keys()
        values = value.values()

        resolved_values = [self.from_proto(v, type_b) for v in values]

        return dict(zip(keys, resolved_values))

    def define_needconvert_fields(self, cls: type[BaseMessage]) -> None:

        args = get_dataclass_fields(cls)

        fields: dict[str, Converter.ConvertResolver] = {}

        for arg in args:
            origin = arg.origin
            inner_args = arg.args

            name = arg.name
            bt = arg.basetype

            if bt and arg.istype(Enum):
                from_ = partial(self._resolve_single_enum_from, type_b=bt)
                to_ = self._resolve_single_enum_to
                fields[name] = Converter.ConvertResolver(
                    from_proto=from_, to_proto=to_, expected_to_proto="Enum"
                )

            elif bt and arg.istype(BaseMessage):
                from_ = partial(self._resolve_single_basemessage_from, type_b=bt)
                to_ = self._resolve_single_basemessage_to
                fields[name] = Converter.ConvertResolver(
                    from_proto=from_, to_proto=to_, expected_to_proto="BaseMessage"
                )

            elif origin:

                if origin is list:
                    bt = inner_args[0]
                    if issubclass(bt, Enum):
                        from_ = partial(self._resolve_list_enum_from, type_b=bt)
                        to_ = self._resolve_list_enum_to
                        fields[name] = Converter.ConvertResolver(
                            from_proto=from_,
                            to_proto=to_,
                            expected_to_proto="list[Enum]",
                        )

                    elif issubclass(bt, BaseMessage):
                        from_ = partial(self._resolve_list_basemessage_from, type_b=bt)
                        to_ = self._resolve_list_basemessage_to
                        fields[name] = Converter.ConvertResolver(
                            from_proto=from_,
                            to_proto=to_,
                            expected_to_proto="list[BaseMessage]",
                        )

                elif origin is dict:
                    bt = inner_args[1]
                    if issubclass(inner_args[1], Enum):
                        from_ = partial(self._resolve_dict_enum_from, type_b=bt)
                        to_ = self._resolve_dict_enum_to
                        fields[name] = Converter.ConvertResolver(
                            from_proto=from_,
                            to_proto=to_,
                            expected_to_proto="dict[Any,Enum]",
                        )

                    elif issubclass(inner_args[1], BaseMessage):
                        from_ = partial(self._resolve_dict_basemessage_from, type_b=bt)
                        to_ = self._resolve_dict_basemessage_to
                        fields[name] = Converter.ConvertResolver(
                            from_proto=from_,
                            to_proto=to_,
                            expected_to_proto="dict[Any,BaseMessage]",
                        )

                elif origin is set:

                    def to_set(x: Iterable[Any]) -> set[Any]:
                        return set(x)

                    fields[name] = Converter.ConvertResolver(
                        from_proto=to_set, to_proto=to_set, expected_to_proto="set[Any]"
                    )
        setattr(cls, "_needconvert", fields)
