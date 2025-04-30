import dataclasses
from collections import defaultdict
from mimetypes import types_map
from typing import Annotated, Any, Optional, Sequence, get_args, get_origin

from makeproto.builder.templates import (
    BaseTemplate,
    EnumTemplate,
    KeyNumber,
    MessageTemplate,
    OneOfTemplate,
    StdFieldTemplate,
)
from makeproto.prototypes import (
    BaseField,
    BaseMessage,
    BaseProto,
    Bool,
    Bytes,
    Enum,
    Float,
    Int64,
    OneOf,
    OneOfKey,
    String,
)


def get_type(field_type: type[Any]):
    if issubclass(field_type, BaseProto):  # type: ignore
        return field_type.prototype()

    def get_default(field_type: type[Any]) -> Optional[str]:

        bclass: Optional[type[BaseField]] = None
        if issubclass(field_type, int):
            bclass = Int64
        if issubclass(field_type, float):
            bclass = Float
        if issubclass(field_type, str):
            bclass = String
        if issubclass(field_type, bytes):
            bclass = Bytes
        if issubclass(field_type, bool):
            bclass = Bool
        if bclass is not None:
            return bclass.prototype()
        return None

    return get_default(field_type)


def get_type_str(field_type: type[Any]) -> Optional[str]:

    origin = get_origin(field_type)
    args = get_args(field_type)
    if origin is Annotated:
        return get_type_str(args[0])

    if origin in {list, set}:
        type_str = get_type(args[0])
        # testar se raise aqui...com list[Path]
        return f"repeated {type_str}"

    if origin is dict:
        key_type, value_type = args
        key_type_str = get_type(key_type)
        value_type_str = get_type(value_type)
        # testar se raise aqui com dict[Path,Counter]
        return f"map<{key_type_str}, {value_type_str}>"

    if not isinstance(field_type, type):  # type: ignore
        # ignorar OneOf
        return

    return get_type(field_type)


def get_oneof_details(field: type[Any]) -> Optional[tuple[OneOfKey, str, Any]]:

    field_type = field.type

    origin = get_origin(field_type)
    args = get_args(field_type)

    ookey = None
    if origin is Annotated:

        def get_oneofkey_by_extra(args: Any) -> OneOfKey:
            ookey = [el for el in args if isinstance(el, OneOfKey)]
            if len(ookey) > 0:
                return ookey[0]
            raise TypeError("tem args mas nao tem oneofkey")

        ookey = get_oneofkey_by_extra(args[1:])
        origin = get_origin(args[0])
        args = get_args(args[0])

    if origin is not OneOf:
        if ookey is None:
            return None
        raise TypeError('Annotated has "OneOfKey", but the type is not "OneOf"')

    str_type = get_type(args[0])
    if str_type is None:
        raise TypeError("base type nao bate")
    if ookey is None:

        def get_oneofkey_by_default(default_: Any) -> OneOfKey:
            if isinstance(default_, OneOfKey):
                return default_
            else:
                raise TypeError("OneOf should have an 'OneOfKey' associated")

        ookey = get_oneofkey_by_default(field.default)

    return ookey, field.name, str_type


def get_templates(cls: type) -> Sequence[BaseTemplate]:

    templates: list[BaseTemplate] = []

    oneofs: dict[str, list[StdFieldTemplate]] = defaultdict(list)

    for f in dataclasses.fields(cls):
        str_temp = get_type_str(f.type)
        if str_temp is not None:
            templates.append(StdFieldTemplate(type=str_temp, name=f.name, number=0))
        else:
            oodetail = get_oneof_details(f)

            if oodetail is not None:
                key, name, type_ = oodetail
                oneofs[key].append(StdFieldTemplate(type_, name, 0))

    for k, v in oneofs.items():
        ootemp = OneOfTemplate(name=k, listed=v)
        templates.append(ootemp)

    return templates


def make_enum_proto_str(field: type[Enum]) -> str:

    values: list[KeyNumber] = []
    for i, e in enumerate(field):
        values.append(KeyNumber(key=e.name, number=i))

    return EnumTemplate(name=field.__name__, listed=values).build()


def make_message_proto_str(cls: type[BaseMessage]) -> str:
    templates = get_templates(cls)
    counter = 1
    for temp in templates:
        counter = temp.set_number(counter)
    temp_str = [t.build().strip("\n") for t in templates]
    return MessageTemplate(name=cls.__name__, fields=temp_str).build()
