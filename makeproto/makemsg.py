import enum
import re
from collections import defaultdict
from typing import Any, Optional, Sequence

from makeproto.mapclass import FuncArg, get_dataclass_fields
from makeproto.prototypes import (
    BaseField,
    BaseMessage,
    BaseProto,
    Bool,
    Bytes,
    Enum,
    FieldOptions,
    Float,
    Int64,
    OneOf,
    OneOfKey,
    String,
)
from makeproto.templates import (
    BaseTemplate,
    EnumTemplate,
    KeyNumber,
    MessageTemplate,
    OneOfTemplate,
    StdFieldTemplate,
)


def get_type(bt: Optional[type[Any]]) -> Optional[str]:

    if bt is None or not isinstance(bt, type):  # type: ignore
        return None

    if issubclass(bt, BaseProto):  # type: ignore
        return bt.prototype()

    if issubclass(bt, enum.Enum):
        return bt.__name__

    def get_default(bt: type[Any]) -> Optional[str]:

        bclass: Optional[type[BaseField]] = None
        if issubclass(bt, int):
            bclass = Int64
        if issubclass(bt, float):
            bclass = Float
        if issubclass(bt, str):
            bclass = String
        if issubclass(bt, bytes):
            bclass = Bytes
        if issubclass(bt, bool):
            bclass = Bool
        if bclass is not None:
            return bclass.prototype()
        return None

    return get_default(bt)


allowed_map_key = [
    "int32",
    "int64",
    "uint32",
    "uint64",
    "sint32",
    "sint64",
    "fixed32",
    "fixed64",
    "sfixed32",
    "sfixed64",
    "bool",
    "string",
]


def get_type_str(arg: FuncArg) -> Optional[str]:

    bt = arg.basetype
    origin = arg.origin
    args = arg.args

    if origin in {list, set}:
        type_str = get_type(args[0])
        if type_str is None:
            return None
        return f"repeated {type_str}"

    if origin is dict:
        key_type, value_type = args
        key_type_str = get_type(key_type)
        value_type_str = get_type(value_type)

        if (
            key_type_str is None
            or value_type_str is None
            or key_type_str not in allowed_map_key
        ):
            return None

        return f"map<{key_type_str}, {value_type_str}>"

    return get_type(bt)


def get_oneof_details(
    arg: FuncArg, snake_case: bool = False
) -> Optional[tuple[OneOfKey, str, Any]]:

    oneofkey = arg.getinstance(OneOfKey, False)

    if arg.origin is not OneOf:
        if oneofkey is not None:
            raise TypeError(
                f"SyntaxError: Field '{arg.name}' has a OneOfKey, but it is not a OneOf"
            )
        return None

    if oneofkey is None:
        raise TypeError(f"OneOf field: '{arg.name}' has no OneOfKey associated")

    if not isinstance(oneofkey, str):  # type: ignore
        raise TypeError(
            f"OneOfKey should be a str. A {type(oneofkey)} was found for arg: {arg.name}."
        )

    args = arg.args
    str_type = get_type(args[0])
    if str_type is None:
        raise TypeError(f"At arg: {arg.name}, OneOf type not allowed: {type(args[0])}")

    name = validate_name(arg.name, snake_case)
    return oneofkey, name, str_type


def to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def validate_name(name: str, snake_case: bool):

    if not name or not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
        raise ValueError(f"Invalid proto identifier: {name}")
    if snake_case:
        name = to_snake(name)
    return name


def get_templates(
    cls: type[Any], snake_camel_mode: bool = False, ignore_error: bool = True
) -> Sequence[BaseTemplate]:

    args = get_dataclass_fields(cls, False)
    templates: list[BaseTemplate] = []

    oneofs: dict[str, list[StdFieldTemplate]] = defaultdict(list)

    for arg in args:
        if arg.basetype is None:
            raise TypeError(f'Arg "{arg.name}" in class "{cls.__name__}" has no type Annotation')
        if arg.has_default:
            raise ValueError(
                f'Data Field cannot have a default value. Found at "{arg.name}"'
            )

        name = validate_name(arg.name, snake_camel_mode)

        str_temp = get_type_str(arg)
        if str_temp is not None:
            options = arg.getinstance(FieldOptions)
            comments, json_name = None, None
            if options is not None:
                comments = options.comments
                json_name = options.json_name
            templates.append(StdFieldTemplate(type=str_temp, name=name, number=0,comments=comments, json_name=json_name))
        else:
            oodetail = get_oneof_details(arg, snake_camel_mode)

            if oodetail is not None:
                key, name_, type_ = oodetail
                name_ = validate_name(name_, snake_camel_mode)
                oneofs[key].append(StdFieldTemplate(type_, name_, 0))
            else:
                if not ignore_error:
                    raise ValueError(f"Invalid Field {arg}")

    for k, v in oneofs.items():
        name_ = validate_name(k, snake_camel_mode)
        ootemp = OneOfTemplate(name=name_, listed=v)
        templates.append(ootemp)

    return templates


def make_message_proto_str(cls: type[BaseMessage]) -> str:
    templates = get_templates(
        cls,
    )
    counter = 1
    for temp in templates:
        counter = temp.set_number(counter)
    temp_str = [t.build().strip("\n") for t in templates]
    return MessageTemplate(name=cls.__name__, fields=temp_str).build()


def make_enum_proto_str(field: type[Enum]) -> str:

    values: list[KeyNumber] = []
    for e in field:
        if not isinstance(e.value, int) or e.value < 0:
            raise TypeError("Enum Values should be positive int only")
        values.append(KeyNumber(key=e.name, number=e.value))

    return EnumTemplate(name=field.__name__, listed=values).build()
