import re
from collections import defaultdict
from typing import Any, Dict, Optional, Sequence, Union

from makeproto.mapclass import FuncArg, get_dataclass_fields
from makeproto.models import Block, EnumBlock, Field, MessageBlock, OneOfBlock
from makeproto.prototypes import (
    DEFAULT_PRIMITIVES,
    BaseMessage,
    BaseProto,
    EnumOption,
    FieldSpec,
    OneOf,
    OneOfKey,
    Enum
)


def get_type(bt: Optional[type[Any]]) -> Optional[str]:

    if bt is None or not isinstance(bt, type):  # type: ignore
        return None

    if issubclass(bt, BaseProto):  # type: ignore
        return bt.prototype()

    if issubclass(bt, Enum):
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


def get_type(bt: Optional[type[Any]]) -> Optional[str]:

    if bt is None or not isinstance(bt, type):  # type: ignore
        return None

    if issubclass(bt, BaseProto):  # type: ignore
        return bt.prototype()

    if issubclass(bt, Enum):
        return bt.__name__

    return DEFAULT_PRIMITIVES.get(bt, None)

def validate_type(bt:Optional[type[Any]]):

    if bt is None or not isinstance(bt, type):  # type: ignore
        return False

    if issubclass(bt, BaseProto):  # type: ignore
        return True

    return bt in DEFAULT_PRIMITIVES


def validate_arg(arg: FuncArg):
    
    bt = arg.basetype
    origin = arg.origin
    args = arg.args

    if origin in {list, set}:
        return validate_type(args[0])
    if origin is dict:
        return validate_type(args[1])

    return validate_type(bt)


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


def check_oneof_consistency(arg: FuncArg) -> Optional[tuple[str, Optional[FieldSpec]]]:

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


def validate_name(name: str, snake_case: bool) -> str:

    if not name or not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
        raise ValueError(f"Invalid proto identifier: {name}")
    if snake_case:
        name = to_snake(name)
    return name


def has_types(args: Sequence[FuncArg], cls_name: str) -> None:

    for arg in args:
        if arg.basetype is None:
            raise TypeError(
                f'Arg "{arg.name}" in class "{cls_name}" has no type Annotation'
            )


def get_spec(
    args: Sequence[FuncArg],
) -> tuple[Optional[str], Optional[Dict[str, Union[str, bool, EnumOption]]]]:

    comment, options = None, None
    for arg in args:

        if arg.has_default:
            if arg.istype(FieldSpec) and isinstance(arg.default, FieldSpec):
                comment = arg.default.comment
                options = arg.default.options
                break
    return comment, options


def make_msgblock(
    cls: type[BaseMessage], snake_camel_mode: bool = False, ignore_error: bool = True
) -> MessageBlock:

    args = get_dataclass_fields(cls, False)

    has_types(args, cls.__name__)

    templates: list[Union[Field, Block[Field]]] = []
    oneofs: dict[str, list[Field]] = defaultdict(list)

    protofile = cls.protofile()
    package = cls.package()

    counter = 1
    for arg in args:

        if arg.has_default and not arg.istype(FieldSpec):
            raise ValueError(
                f'Data Field cannot have a default value. Found at "{arg.name}"'
            )

        # name = validate_name(arg.name, snake_camel_mode)

        str_temp = get_type_str(arg)

        if str_temp is not None:
            specs = arg.getinstance(FieldSpec, default=False)
            comment, options = None, None
            if specs is not None:
                comment = specs.comment
                options = specs.options
            field = Field.make(
                name=arg.name,
                number=counter,
                ftype=str_temp,
                comment=comment,
                options=options,
            )
            counter += 1
            templates.append(field)
        else:
            oodetail = get_oneof_details(arg)

            if oodetail is not None:
                key, name_, ftype, specs = oodetail
                # name_ = validate_name(name_, snake_camel_mode)
                comment, options = None, None
                if specs is not None:
                    comment = specs.comment
                    options = specs.options
                oo_field = Field.make(
                    name=name_,
                    number=counter,
                    ftype=ftype,
                    comment=comment,
                    options=options,
                )
                counter += 1
                oneofs[key].append(oo_field)
            else:
                if not ignore_error:
                    raise ValueError(f"Invalid Field {arg}")

    for k, v in oneofs.items():
        # name_ = validate_name(k, snake_camel_mode)
        ootemp: OneOfBlock = Block.make(
            protofile=protofile,
            package=package,
            name=k,
            block_type="oneof",
            fields=v,
        )
        templates.append(ootemp)

    comment, options = get_spec(args)

    block: MessageBlock = Block.make(
        protofile=protofile,
        package=package,
        name=cls.__name__,
        block_type="message",
        fields=templates,
        comment=comment,
        options=options,
    )

    return block

def get_oneof_details2(
    arg: FuncArg,
) -> Optional[tuple[str, str, Any, Optional[FieldSpec]]]:

    oneof = check_oneof_consistency(arg)
    if oneof is None:
        return None
    oneofkey, spec = oneof

    args = arg.args
    isvalid = validate_type(args[0])
    if isvalid :
        raise TypeError(f"At arg: {arg.name}, OneOf type not allowed: {type(args[0])}")

    return oneofkey, arg.name, args[0], spec



def make_msgblock2(cls: type[BaseMessage], ignore_error: bool = True) -> MessageBlock:

    args = get_dataclass_fields(cls, False)

    has_types(args, cls.__name__)

    templates: list[Union[Field, Block[Field]]] = []
    oneofs: dict[str, list[Field]] = defaultdict(list)

    protofile = cls.protofile()
    package = cls.package()

    counter = 1
    for arg in args:

        if arg.has_default and not arg.istype(FieldSpec):
            raise ValueError(
                f'Data Field cannot have a default value. Found at "{arg.name}"'
            )

        isvalid = validate_arg(arg)

        if isvalid:
            specs = arg.getinstance(FieldSpec, default=False)
            comment, options = None, None
            if specs is not None:
                comment = specs.comment
                options = specs.options
            field = Field.make(
                name=arg.name,
                number=counter,
                ftype=bt,
                comment=comment,
                options=options,
            )
            counter += 1
            templates.append(field)
        else:
            oodetail = get_oneof_details2(arg)

            if oodetail is not None:
                key, name_, ftype, specs = oodetail
                comment, options = None, None
                if specs is not None:
                    comment = specs.comment
                    options = specs.options
                oo_field = Field.make(
                    name=name_,
                    number=counter,
                    ftype=ftype,
                    comment=comment,
                    options=options,
                )
                counter += 1
                oneofs[key].append(oo_field)
            else:
                if not ignore_error:
                    raise ValueError(f"Invalid Field {arg}")

    for k, v in oneofs.items():
        # name_ = validate_name(k, snake_camel_mode)
        ootemp: OneOfBlock = Block.make(
            protofile=protofile,
            package=package,
            name=k,
            block_type="oneof",
            fields=v,
        )
        templates.append(ootemp)

    comment, options = get_spec(args)

    block: MessageBlock = Block.make(
        protofile=protofile,
        package=package,
        name=cls.__name__,
        block_type="message",
        fields=templates,
        comment=comment,
        options=options,
    )

    return block


def make_enumblock(enum: type[Enum]) -> EnumBlock:

    fields: list[Field] = []

    protofile = enum.protofile()
    package = enum.package()

    for member in enum:
        name, value = member.name, member.value
        if not isinstance(value, int) or value < 0:
            raise TypeError(f"Enum Values should be positive int only. got {value}")
        fields.append(Field.make(name, value))

    enumBlock: EnumBlock = Block.make(protofile=protofile,package=package,
        name=enum.__name__, block_type="enum", fields=fields
    )
    return enumBlock


def cls_to_blocks(
    tgt: type[Union[BaseMessage, Enum]],
    visited: Optional[set[Union[MessageBlock, EnumBlock]]] = None,
) -> set[Union[MessageBlock, EnumBlock]]:

    if not isinstance(tgt, type):  # type: ignore
        raise TypeError(f'tgt argumento should be a type. found "{tgt}"')

    if visited is None:
        visited = set()

    # Evita regenerar blocos que já foram criados
    if any(b.name == tgt.__name__ for b in visited):
        return visited

    if issubclass(tgt, Enum):
        enumblock = make_enumblock(tgt)
        visited.add(enumblock)

    elif issubclass(tgt, BaseMessage):  # type: ignore
        msgblock = make_msgblock(tgt, False, False)
        visited.add(msgblock)

        args = get_dataclass_fields(tgt, False)

        for arg in args:
            if arg.istype(Enum) or arg.istype(BaseMessage):
                msgs = cls_to_blocks(arg.basetype, visited)
                visited.update(msgs)

    return visited
