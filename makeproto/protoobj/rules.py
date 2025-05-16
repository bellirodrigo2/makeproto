from typing import Any, List

from makeproto.mapclass import FuncArg
from makeproto.protoobj.base import FieldSpec, OneOf
from makeproto.protoobj.types import DEFAULT_PRIMITIVES, BaseProto, allowed_map_key

# ---------------- Validate Class Type vs Proto Types ----------------------


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


# ---------------- Validate FieldSpec ---------------------------------------


def check_field_spec(
    spec: FieldSpec, field_name: str, field: bool = True
) -> List[Exception]:

    exceptions: List[Exception] = []

    what, on = ("Field", "on Field") if field else ("Class", "")

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
