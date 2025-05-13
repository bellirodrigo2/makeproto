from dataclasses import dataclass
from typing import List, Optional

import pytest

from makeproto.exceptions import ProtoBlockError
from makeproto.makeblock import make_method
from makeproto.models import Method
from makeproto.prototypes import BaseMessage


@dataclass
class MyRequest(BaseMessage):
    pass


@dataclass
class MyResponse(BaseMessage):
    pass


@dataclass
class NotAMessage:
    pass


# Simulações de mensagens válidas


@dataclass
class Req(BaseMessage):
    pass


@dataclass
class Res(BaseMessage):
    pass


# Inválido para testes negativos


@dataclass
class InvalidType:
    pass


# -------------------- Testes de sucesso --------------------


def test_make_method_simple_function() -> None:

    method = make_method("handler", Req, Res, False, False)

    assert isinstance(method, Method)
    assert method.method_name == "handler"
    assert method.request_type == Req
    assert method.response_type == Res
    assert method.response_stream is False


# -------------------- Testes de erro --------------------


def test_make_method_missing_type() -> None:

    with pytest.raises(ProtoBlockError, match="1 Errors found on method"):
        make_method("handler", Req, None, False, False)
    with pytest.raises(
        ProtoBlockError, match="Error on response argument type. Argument type is None"
    ):
        make_method("handler", Req, None, False, False)

    with pytest.raises(ProtoBlockError, match="1 Errors found on method"):
        make_method("handler", None, Res, False, False)
    with pytest.raises(
        ProtoBlockError, match="Error on request argument type. Argument type is None"
    ):
        make_method("handler", None, Res, False, False)


def test_make_method_invalid_request_type() -> None:
    with pytest.raises(ProtoBlockError, match="Argument is not a BaseMessage"):
        make_method("handler", InvalidType, Res, False, False)


def test_make_method_invalid_response_type() -> None:

    with pytest.raises(ProtoBlockError, match="Argument is not a BaseMessage"):
        make_method("handler", Req, InvalidType, False, False)


def test_make_method_request_type_has_origin() -> None:

    with pytest.raises(ProtoBlockError, match="Argument is not a type"):
        make_method("handler", List[Req], Res, False, False)
    with pytest.raises(ProtoBlockError, match="Argument is not a type"):
        make_method("handler", Req, Optional[Res], False, False)


def test_make_method_request_notype() -> None:

    with pytest.raises(ProtoBlockError, match="Argument is not a type"):
        make_method("handler", "List[Req]", Res, False, False)
    with pytest.raises(ProtoBlockError, match="Argument is not a type"):
        make_method("handler", Req, "Optional[Res]", False, False)
