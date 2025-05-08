import inspect
from typing import Any, Callable, Dict, Optional,  Union, get_type_hints

from makeproto.models import Method
from makeproto.prototypes import BaseMessage


def check_request_consistency(arg_type: type[Any], funcname:str, req_or_resp:str):

    def get_error_msg(reason: str):
        raise TypeError(
            f"Error on {req_or_resp} argument type for method '{funcname}'. {reason}"
        )

    if arg_type is None: # type: ignore
        get_error_msg("Argument type is None")

    if not isinstance(arg_type, type): # type: ignore
        get_error_msg(f"Argument is not a type: {type(arg_type)}")

    if not issubclass(arg_type, BaseMessage):
        get_error_msg(
            f"Argument is not a BaseMessage: {type(arg_type)}",
        )

def make_method(
    func: Callable[..., Any],
    request_type: type[Any],
    request_stream: bool,
    options:Optional[Dict[str,Union[str,bool]]]=None,
    comment:Optional[str]=None
) -> Method:

    method_name = func.__name__

    check_request_consistency(request_type, method_name, 'request')

    hints = get_type_hints(func)
    response_type = hints.get("return", None)
    if response_type is None:
        raise TypeError(f"Function {method_name} has no typed return")

    check_request_consistency(response_type, method_name, 'response')

    response_stream:bool = inspect.isgeneratorfunction(func) or inspect.isasyncgenfunction(
        func
    )

    return Method.make(
        method_name=method_name,
        request_type=request_type.__name__,
        response_type=response_type.__name__,
        request_stream=request_stream,
        response_stream=response_stream,
        comment=comment,
        options=options
    )
