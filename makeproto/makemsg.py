import enum
import re
from collections import defaultdict
from typing import Any, Optional, Union

from makeproto.mapclass import FuncArg, get_dataclass_fields
from makeproto.models import Block, EnumBlock, Field, MessageBlock, OneOfBlock
from makeproto.prototypes import (
    DEFAULT_PRIMITIVES,
    BaseProto,
    FieldSpec,
    OneOf,
    OneOfKey,
)


def get_type(bt: Optional[type[Any]]) -> Optional[str]:

    if bt is None or not isinstance(bt, type):  # type: ignore
        return None

    if issubclass(bt, BaseProto):  # type: ignore
        return bt.prototype()

    if issubclass(bt, enum.Enum):
        return bt.__name__

    return DEFAULT_PRIMITIVES.get(bt, None)


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


def check_oneof_consistency(arg: FuncArg):

    oneofkey = arg.getinstance(OneOfKey, False)

    if arg.origin is not OneOf:
        if oneofkey is not None:
            raise TypeError(
                f"SyntaxError: Field '{arg.name}' has a OneOfKey, but it is not a OneOf"
            )
        return None

    if oneofkey is None:
        raise TypeError(f"OneOf field: '{arg.name}' has no OneOfKey associated")

    return oneofkey.key, oneofkey.spec


def get_oneof_details(
    arg: FuncArg,
) -> Optional[tuple[str, str, Any, Optional[FieldSpec]]]:

    oneof = check_oneof_consistency(arg)
    if oneof is None:
        return None
    oneofkey, spec = oneof

    args = arg.args
    str_type = get_type(args[0])
    if str_type is None:
        raise TypeError(f"At arg: {arg.name}, OneOf type not allowed: {type(args[0])}")

    return oneofkey, arg.name, str_type, spec


def to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def validate_name(name: str, snake_case: bool):

    if not name or not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
        raise ValueError(f"Invalid proto identifier: {name}")
    if snake_case:
        name = to_snake(name)
    return name


def make_msgblock(
    cls: type[Any], snake_camel_mode: bool = False, ignore_error: bool = True
) -> MessageBlock:

    args = get_dataclass_fields(cls, False)

    templates: list[Union[Field, Block[Field]]] = []
    oneofs: dict[str, list[Field]] = defaultdict(list)

    comment, options = None, None

    counter = 1
    for arg in args:

        if arg.basetype is None:
            raise TypeError(
                f'Arg "{arg.name}" in class "{cls.__name__}" has no type Annotation'
            )

        if arg.has_default:
            if arg.istype(FieldSpec) and isinstance(arg.default, FieldSpec):
                comment = arg.default.comment
                options = arg.default.options
                continue
            raise ValueError(
                f'Data Field cannot have a default value. Found at "{arg.name}"'
            )

        name = validate_name(arg.name, snake_camel_mode)

        str_temp = get_type_str(arg)

        if str_temp is not None:
            specs = arg.getinstance(FieldSpec, default=False)
            comment, options = None, None
            if specs is not None:
                comment = specs.comment
                options = specs.options
            field = Field.make(
                name=name,
                number=counter,
                type_=str_temp,
                comment=comment,
                options=options,
            )
            counter += 1
            templates.append(field)
        else:
            oodetail = get_oneof_details(arg)

            if oodetail is not None:
                key, name_, type_, specs = oodetail
                name_ = validate_name(name_, snake_camel_mode)
                comment, options = None, None
                if specs is not None:
                    comment = specs.comment
                    options = specs.options
                oo_field = Field.make(
                    name=name_,
                    number=counter,
                    type_=type_,
                    comment=comment,
                    options=options,
                )
                counter += 1
                oneofs[key].append(oo_field)
            else:
                if not ignore_error:
                    raise ValueError(f"Invalid Field {arg}")

    for k, v in oneofs.items():
        name_ = validate_name(k, snake_camel_mode)
        ootemp: OneOfBlock = Block.make(name=name_, block_type="oneof", fields=v)
        templates.append(ootemp)

    block: MessageBlock = Block.make(
        name=cls.__name__,
        block_type="message",
        fields=templates,
        comment=comment,
        options=options,
    )

    return block


def make_enumblock(enum: type[enum.Enum]) -> EnumBlock:

    fields: list[Field] = []

    for member in enum:
        name, value = member.name, member.value
        if not isinstance(value, int) or value < 0:
            raise TypeError(f"Enum Values should be positive int only. got {value}")
        fields.append(Field.make(name, value))

    enumBlock: EnumBlock = Block.make(
        name=enum.__name__, block_type="enum", fields=fields
    )
    return enumBlock
