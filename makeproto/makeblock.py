from collections import defaultdict
from enum import Enum
from typing import Any, List, Optional, Set

from makeproto.exceptions import ProtoBlockError
from makeproto.mapclass import FuncArg, map_class_fields
from makeproto.models import Block, Field, Method
from makeproto.prototypes import (
    DEFAULT_PRIMITIVES,
    BaseMessage,
    BaseProto,
    FieldSpec,
    OneOf,
    ProtoOption,
    allowed_map_key,
)


def check_type(bt: type[Any], arg_name: str) -> None | TypeError:

    if not isinstance(bt, type):  # type: ignore
        return TypeError(f'Field "{arg_name}" is not a type. Found {bt}')

    if issubclass(bt, BaseProto):  # type: ignore
        return None

    if bt not in DEFAULT_PRIMITIVES:
        return TypeError(f'Field "{arg_name}" type is not allowed. Found {bt}')

    return None


def check_arg(arg: FuncArg) -> TypeError | None:

    if arg.basetype is None:
        return TypeError(f'Field "{arg.name}" has no type Annotation')

    bt = arg.basetype
    origin = arg.origin
    args = arg.args

    if origin is list:
        return check_type(args[0], arg.name)

    if origin is dict:
        if args[0] in allowed_map_key:
            return check_type(args[1], arg.name)
        return TypeError(
            f'Field "{arg.name}" is a dict with not allowed key type. Found "{args[0]}" as dict key'
        )

    return check_type(bt, arg.name)


def check_field_spec(
    spec: FieldSpec, field_name: str, field: bool = True
) -> List[Exception]:

    exceptions: List[Exception] = []

    what = "Field" if field else "Class"
    on = "on Field" if field else ""

    def err_msg(err_type: str, found: Any) -> str:
        return f'{what} "{field_name}" {err_type} {on} has a wrong type. Found {found}'

    comment = spec.comment
    if comment is not None and not isinstance(comment, str):
        err = TypeError(err_msg("comment", comment))
        exceptions.append(err)

    options = spec.options
    if options is not None:
        if not isinstance(options, dict):
            err = TypeError(err_msg("options", options))
            exceptions.append(err)
        else:
            for k, v in options.items():
                if not isinstance(k, str):
                    err = TypeError(err_msg("options", k))
                    exceptions.append(err)
                if not isinstance(v, bool) and not isinstance(v, str):
                    err = TypeError(err_msg("options", v))
                    exceptions.append(err)
    index = spec.index
    if not isinstance(index, int) or index < 0:
        err = TypeError(err_msg("index", index))
        exceptions.append(err)
    if isinstance(spec, OneOf) and not isinstance(spec.key, str):
        err = TypeError(err_msg("key", spec.key))
        exceptions.append(err),

    return exceptions


def make_msgblock(cls: type[BaseMessage]) -> Block:

    args = map_class_fields(cls, False)

    fields: set[Block] = set()
    oneofs: dict[str, set[Field]] = defaultdict(set)

    exceptions: List[Exception] = []

    for arg in args:
        exception = check_arg(arg)
        if exception is not None:
            exceptions.append(exception)
            continue
        comment = ""
        options = ProtoOption()
        index = 0

        spec = arg.getinstance(FieldSpec, True)
        if spec is not None:
            comment = spec.comment
            options = spec.options
            index = spec.index

            spec_exceptions = check_field_spec(spec, arg.name)
            exceptions.extend(spec_exceptions)

        field = Field(
            name=arg.name,
            ftype=arg.basetype,
            comment=comment,
            options=options,
            number=index,
        )

        if isinstance(spec, OneOf):
            key = spec.key
            oneofs[key].add(field)
        else:
            fields.add(field)

    protofile = cls.protofile
    package = cls.package
    comment = cls.comment
    options = cls.options
    reserved = cls.reserved

    block_spec = FieldSpec(comment=comment, options=options)
    spec_exceptions = check_field_spec(block_spec, cls.__name__, False)
    exceptions.extend(spec_exceptions)

    # falta checar reserved

    for k, v in oneofs.items():
        # como pegar options e comments em nivel de block ?
        ootemp = Block(
            protofile=protofile,
            package=package,
            name=k,
            block_type="oneof",
            fields=v,
            comment="",
            options=ProtoOption(),
            reserved=[],
        )
        fields.add(ootemp)

    if exceptions:
        raise ProtoBlockError(cls.__name__, "class", exceptions)

    block = Block(
        protofile=protofile,
        package=package,
        name=cls.__name__,
        block_type="message",
        fields=fields,
        comment=comment,
        options=options,
        reserved=reserved,
    )

    return block


def make_enumblock(enum: type[BaseMessage]) -> Block:

    exceptions: List[Exception] = []

    if not isinstance(enum, type) or not issubclass(enum, Enum):
        err = TypeError(
            f'Class "{enum.__name__}" is not an Enum, on make_enumblock function'
        )
        exceptions.append(err)

    fields: Set[Field] = set()

    for member in enum:
        name, value = member.name, member.value
        if not isinstance(value, int) or value < 0:
            err = TypeError(f"Enum Values should be positive int only. got {value}")
            exceptions.append(err)
        fields.add(
            Field(
                name=name, number=value, ftype=None, comment="", options=ProtoOption()
            )
        )

    protofile = enum.protofile
    package = enum.package
    comment = enum.comment
    options = enum.options
    reserved = enum.reserved

    block_spec = FieldSpec(comment=comment, options=options)
    spec_exceptions = check_field_spec(block_spec, enum.__name__, False)
    exceptions.extend(spec_exceptions)

    if exceptions:
        raise ProtoBlockError(enum.__name__, "Enum", exceptions)

    enumBlock: Block = Block(
        protofile=protofile,
        package=package,
        name=enum.__name__,
        block_type="enum",
        fields=fields,
        comment=comment,
        options=options,
        reserved=reserved,
    )
    return enumBlock


def cls_to_blocks(
    tgt: type[BaseMessage],
    visited: Optional[set[Block]] = None,
) -> set[Block]:

    if not isinstance(tgt, type):  # type: ignore
        raise TypeError(f'tgt argumento should be a type. found "{tgt}"')

    if visited is None:
        visited: Set[Block] = set()

    # Evita regenerar blocos que já foram criados
    if any(b.name == tgt.__name__ for b in visited):
        return visited

    if issubclass(tgt, Enum):
        enumblock = make_enumblock(tgt)
        visited.add(enumblock)

    elif issubclass(tgt, BaseMessage):  # type: ignore
        msgblock = make_msgblock(tgt)
        visited.add(msgblock)

        args = map_class_fields(tgt, False)

        for arg in args:
            if arg.istype(Enum) or arg.istype(BaseMessage):
                msgs = cls_to_blocks(arg.basetype, visited)
                visited.update(msgs)

    return visited


def check_request_consistency(
    arg_type: type[Any], req_or_resp: str
) -> Optional[Exception]:

    def get_error_msg(reason: str) -> Exception:
        return TypeError(f"Error on {req_or_resp} argument type. {reason}")

    if arg_type is None:  # type: ignore
        return get_error_msg("Argument type is None")

    if not isinstance(arg_type, type):  # type: ignore
        return get_error_msg(f"Argument is not a type: {arg_type}")

    if not issubclass(arg_type, BaseMessage):
        return get_error_msg(
            f"Argument is not a BaseMessage: {arg_type}",
        )
    return None


def make_method(
    method_name: str,
    request_type: type[Any],
    response_type: type[Any],
    request_stream: bool,
    response_stream: bool,
    options: Optional[ProtoOption] = None,
    comment: Optional[str] = None,
) -> Method:

    exceptions: List[Exception] = []

    req_exc = check_request_consistency(request_type, "request")
    if req_exc:
        exceptions.append(req_exc)
    resp_exc = check_request_consistency(response_type, "response")
    if resp_exc:
        exceptions.append(resp_exc)

    block_spec = FieldSpec(comment=comment or "", options=options)
    spec_exceptions = check_field_spec(block_spec, method_name, False)
    exceptions.extend(spec_exceptions)

    if exceptions:
        raise ProtoBlockError(method_name, "method", exceptions)

    return Method(
        method_name=method_name,
        request_type=request_type,
        response_type=response_type,
        request_stream=request_stream,
        response_stream=response_stream,
        comment=comment or "",
        options=options or ProtoOption(),
    )
