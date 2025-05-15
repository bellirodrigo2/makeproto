from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union

from makeproto.exceptions import ProtoBlockError
from makeproto.indexer import Indexer
from makeproto.mapclass import FuncArg, map_class_fields
from makeproto.prototypes import (
    DEFAULT_PRIMITIVES,
    BaseMessage,
    BaseProto,
    FieldSpec,
    OneOf,
    ProtoOption,
    allowed_map_key,
)
from makeproto.tempmodels import Block, Field, Method


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
    if isinstance(spec, OneOf) and not isinstance(spec.key, str):
        err = TypeError(err_msg("key", spec.key))
        exceptions.append(err),

    return exceptions


def get_module(
    cls: type[BaseMessage],
) -> Tuple[Optional[str], Optional[str]]:
    protofile_method = getattr(cls, "protofile", None)
    protofile: Optional[str] = None if protofile_method is None else protofile_method()

    package_method = getattr(cls, "package", None)
    package: Optional[str] = None if package_method is None else package_method()

    return protofile, package


def get_comment_options(
    cls: type[BaseMessage],
) -> Tuple[str, ProtoOption]:
    comment_method = getattr(cls, "comment", None)
    comment: str = "" if comment_method is None else comment_method()

    options_method = getattr(cls, "options", None)
    options: ProtoOption = ProtoOption() if options_method is None else options_method()

    return comment, options


def get_headers(
    cls: type[BaseMessage], default_protofile: str, default_package: str
) -> Tuple[Optional[str], Optional[str], str, ProtoOption, List[Any]]:

    protofile, package = get_module(cls)
    if protofile is None:
        protofile = default_protofile
    if package is None:
        package = default_package

    comment, options = get_comment_options(cls)

    reserved_method = getattr(cls, "reserved", None)
    reserved: List[Union[int, range]] = (
        [] if reserved_method is None else reserved_method()
    )
    return protofile, package, comment, options, reserved


def handle_findex(
    findex: int, indexer: Indexer, exceptions: List[Exception], name: str
) -> int:

    if not isinstance(findex, int):
        err = TypeError(f'Field "{name}" has a non integer index: "{findex}"')
        exceptions.append(err)
        return findex

    def is_in_index_range(number: int) -> bool:
        return 1 <= number <= 536870911

    if findex == 0:
        findex = indexer.next
    elif findex in indexer or findex < indexer.current:
        exceptions.append(
            ValueError(f'Field "{name}" has an index of: "{findex}" which is reserved')
        )
    elif not is_in_index_range(findex):
        ValueError(
            f'Field "{name}" has an index of: "{findex}" which is out of range (from 0 to 536870911)'
        )

    return findex


def get_field_spec(arg: FuncArg, exceptions: List[Exception]) -> Optional[FieldSpec]:
    spec = arg.getinstance(FieldSpec, True)
    if spec is not None:
        spec_exceptions = check_field_spec(spec, arg.name)
        exceptions.extend(spec_exceptions)
    return spec


def make_msgblock(
    cls: type[BaseMessage], default_protofile: str, default_package: str
) -> Block:

    args = map_class_fields(cls, False)

    exceptions: List[Exception] = []

    protofile, package, comment, options, reserved = get_headers(
        cls, default_protofile, default_package
    )

    block_spec = FieldSpec(comment=comment, options=options)
    spec_exceptions = check_field_spec(block_spec, cls.__name__, False)
    exceptions.extend(spec_exceptions)

    running_index = Indexer(idxs=reserved)
    running_index.reserve(range(1900, 1999))  # reserved by google

    fields: List[Block] = []
    oneofs: Dict[str, List[Field]] = defaultdict(list)

    for arg in args:

        exception = check_arg(arg)
        if exception is not None:
            exceptions.append(exception)
            continue

        spec = get_field_spec(arg, exceptions)
        fcomment = spec.comment if spec is not None else ""
        foptions = spec.options if spec is not None else ProtoOption()
        findex = spec.index if spec is not None else 0

        findex = handle_findex(findex, running_index, exceptions, arg.name)

        field = Field(
            name=arg.name,
            ftype=arg.basetype,
            comment=fcomment,
            options=foptions,
            number=findex,
        )

        if spec is not None and isinstance(spec, OneOf):
            key = spec.key
            oneofs[key].append(field)
        else:
            fields.append(field)

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
            reserved=str([]),
        )
        fields.append(ootemp)

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
        reserved=str(reserved),
    )

    return block


def make_enumblock(
    enum: type[BaseMessage], default_protofile: str, default_package: str
) -> Block:

    exceptions: List[Exception] = []

    if not isinstance(enum, type) or not issubclass(enum, Enum):
        err = TypeError(
            f'Class "{enum.__name__}" is not an Enum, on make_enumblock function'
        )
        exceptions.append(err)

    fields: List[Field] = []

    for member in enum:
        name, value = member.name, member.value
        if not isinstance(value, int) or value < 0:
            err = TypeError(f"Enum Values should be positive int only. got {value}")
            exceptions.append(err)
        fields.append(
            Field(
                name=name, number=value, ftype=None, comment="", options=ProtoOption()
            )
        )

    protofile, package, comment, options, reserved = get_headers(
        enum, default_protofile, default_package
    )
    if protofile is None:
        protofile = default_protofile
    if package is None:
        package = default_package

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


def cls_map(
    tgt: type[BaseMessage],
    default_protofile: str,
    default_package: str,
    visited: Optional[Set[Block]] = None,
) -> Set[BaseMessage]:

    if not isinstance(tgt, type):  # type: ignore
        raise TypeError(f'tgt argumento should be a type. found "{tgt}"')

    if visited is None:
        visited: Set[BaseMessage] = set()

    # Evita regenerar blocos que já foram criados
    if any(b.__name__ == tgt.__name__ for b in visited):
        return visited

    if issubclass(tgt, Enum) or issubclass(tgt, BaseMessage):
        visited.add(tgt)

        args = map_class_fields(tgt, False)

        for arg in args:
            bt = arg.basetype
            if arg.istype(BaseMessage):
                protofile, package = get_module(bt)
                msgs = cls_map(
                    arg.basetype,
                    protofile or default_protofile,
                    package or default_package,
                    visited,
                )
                visited.update(msgs)

    return visited


def cls_to_blocks(
    tgt: type[BaseMessage],
    default_protofile: str,
    default_package: str,
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
        enumblock = make_enumblock(tgt, default_protofile, default_package)
        visited.add(enumblock)

    elif issubclass(tgt, BaseMessage):  # type: ignore
        msgblock = make_msgblock(tgt, default_protofile, default_package)
        visited.add(msgblock)

        args = map_class_fields(tgt, False)

        for arg in args:
            bt = arg.basetype
            if arg.istype(BaseMessage):
                protofile, package = get_module(bt)
                msgs = cls_to_blocks(
                    arg.basetype,
                    protofile or default_protofile,
                    package or default_package,
                    visited,
                )
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
