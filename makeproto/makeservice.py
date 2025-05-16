from typing import Any, List, Optional

from makeproto.exceptions import ProtoBlockError
from makeproto.protoobj.base import FieldSpec, ProtoOption
from makeproto.protoobj.message import BaseMessage
from makeproto.protoobj.rules import check_field_spec
from makeproto.template_models import Method


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
