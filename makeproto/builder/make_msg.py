import dataclasses
from collections import defaultdict
from mimetypes import types_map
import re
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


def get_type(field_type: type[Any], raise_on_type_error:bool=False):
    
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

    default_= get_default(field_type)

    if raise_on_type_error and default_ is None:
        raise ValueError(f'Base Type not allowed: {type(field_type)}')

    return default_

allowed_map_key = [
    'int32',
    'int64',
    'uint32',
    'uint64',
    'sint32',
    'sint64',
    'fixed32',
    'fixed64',
    'sfixed32',
    'sfixed64',
    'bool',
    'string'
]

def get_type_str(field_type: type[Any], raise_on_type_error:bool=False) -> Optional[str]:
    origin = get_origin(field_type)
    args = get_args(field_type)
    if origin is Annotated:
        return get_type_str(args[0])

    if origin in {list, set}:
        type_str = get_type(args[0])
        if type_str is None:
            raise ValueError(f'List type cannot be {type(type_str)}')
        return f"repeated {type_str}"

    if origin is dict:
        key_type, value_type = args
        key_type_str = get_type(key_type)
        value_type_str = get_type(value_type)

        if key_type_str is None or key_type_str not in allowed_map_key:
            raise ValueError(f'Map key cannot be {type(value_type)}')
        if value_type_str is None:
            raise ValueError(f'Map value cannot be {type(key_type)}')

        return f"map<{key_type_str}, {value_type_str}>"

    if not isinstance(field_type, type):  # type: ignore
        origin = get_origin(field_type)
        if not raise_on_type_error or origin is OneOf:
            return None
        raise ValueError(f'Base Type not allowed: {origin}')

    return get_type(field_type,raise_on_type_error)


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
        raise TypeError(f"OneOf type is not allowed {type(args[0])}")
    if ookey is None:

        def get_oneofkey_by_default(default_: Any) -> OneOfKey:
            if isinstance(default_, OneOfKey):
                return default_
            else:
                raise TypeError("OneOf should have an 'OneOfKey' associated")

        ookey = get_oneofkey_by_default(field.default)

    return ookey, field.name, str_type

def to_snake(name:str)->str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

def validate_name(name:str, snake_case:bool):
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
        raise ValueError(f"Invalid proto identifier: {name}")
    if snake_case:
        name = to_snake(name)
    return name

# oneof_proibido, repeated, map outro oneof

# impedir 
# @dataclass 
# class int32(BaseMessage):...

def get_templates(cls: type, snake_camel_mode:bool=False) -> Sequence[BaseTemplate]:

    templates: list[BaseTemplate] = []

    oneofs: dict[str, list[StdFieldTemplate]] = defaultdict(list)


    for f in dataclasses.fields(cls):
    
        name = validate_name(f.name, snake_camel_mode)

        str_temp = get_type_str(f.type)
        if str_temp is not None:
            templates.append(StdFieldTemplate(type=str_temp, name=name, number=0))
        else:
            oodetail = get_oneof_details(f)

            if oodetail is not None:
                key, name_, type_ = oodetail
                name_ = validate_name(name_, snake_camel_mode)
                oneofs[key].append(StdFieldTemplate(type_, name_, 0))

    for k, v in oneofs.items():
        name_ = validate_name(k, snake_camel_mode)
        ootemp = OneOfTemplate(name=name_, listed=v)
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
