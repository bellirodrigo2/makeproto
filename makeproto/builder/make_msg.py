import dataclasses
from collections import defaultdict
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


def get_type_str(field_type: type[Any]) -> Optional[str]:

    origin = get_origin(field_type)
    args = get_args(field_type)
    if origin is Annotated:
        return get_type_str(args[0])

    if origin in {list, set}:
        return f"repeated {get_type_str(args[0])}"

    if origin is dict:
        key_type, value_type = args
        return f"map<{get_type_str(key_type)}, {get_type_str(value_type)}>"

    if not isinstance(field_type, type):
        # ignorar OneOf
        return

    if issubclass(field_type, BaseProto):  # type: ignore
        return field_type.prototype()

    return get_default(field_type)


def get_oneof_details(
    field: dataclasses.Field[Any],
) -> Optional[tuple[OneOfKey, str, Any]]:

    field_type = field.type

    origin = get_origin(field_type)
    args = get_args(field_type)

    details = None
    if origin is Annotated:
        ftype, *extras = args
        origin_inner = get_origin(ftype)
        args_inner = get_args(ftype)
        # recursivo
        # passar extras deve ter OneOfKey
        if isinstance(origin_inner, type) and issubclass(origin_inner, OneOf):

            ootype = args_inner[0]
            ookey = [el for el in extras if isinstance(el, OneOfKey)]
            if len(ookey) > 0:
                details = (ookey[0], field.name, ootype)
            else:
                raise TypeError('Annotated "OneOf", should have a OneOfKey on extras')
        else:
            if [el for el in extras if isinstance(el, OneOfKey)]:
                raise TypeError("XXX")
    elif origin is OneOf:
        # aqui, falta checar se eh BaseField ou basetypes, str, int, etc...pode list ?
        # origin deve ter prototype ou get_default
        # se extras for passado use...
        # ou entao default'
        origin_inner = get_origin(args)
        ootype = args[0]
        default_ = field.default
        if isinstance(default_, OneOfKey):
            details = (default_, field.name, ootype)
        else:
            raise TypeError("OneOf should have an 'OneOfKey' associated")
    return details


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
    temp_str = [t.build().strip("\n") for t in templates]
    return MessageTemplate(name=cls.__name__, fields=temp_str).build()
