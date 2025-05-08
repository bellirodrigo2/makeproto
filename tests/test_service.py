

from dataclasses import dataclass
import pytest
from makeproto.makeservice import make_method, check_request_consistency
from makeproto.prototypes import BaseMessage
from makeproto.models import Method

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
class Req(BaseMessage): pass

@dataclass
class Res(BaseMessage): pass

# Inválido para testes negativos

@dataclass
class InvalidType: pass


# -------------------- Testes de sucesso --------------------

def test_make_method_simple_function():
    def handler(req: Req) -> Res:
        return Res()

    method = make_method(handler, Req, request_stream=False)

    assert isinstance(method, Method)
    assert method.method_name == "handler"
    assert method.request_type == "Req"
    assert method.response_type == "Res"
    assert method.response_stream is False


def test_make_method_with_generator_function():
    def handler(req: Req) -> Res:
        yield Res()

    method = make_method(handler, Req, request_stream=False)
    assert method.response_stream is True


def test_make_method_with_async_generator():
    async def handler(req: Req) -> Res:
        yield Res()

    method = make_method(handler, Req, request_stream=False)
    assert method.response_stream is True


# -------------------- Testes de erro --------------------

def test_make_method_missing_return_type():
    def handler(req: Req):
        return Res()

    with pytest.raises(TypeError, match="has no typed return"):
        make_method(handler, Req, request_stream=False)


def test_make_method_invalid_request_type():
    def handler(req: InvalidType) -> Res:
        return Res()

    with pytest.raises(TypeError, match="Argument is not a BaseMessage"):
        make_method(handler, InvalidType, request_stream=False)


def test_make_method_invalid_response_type():
    def handler(req: Req) -> InvalidType:
        return InvalidType()

    with pytest.raises(TypeError, match="Argument is not a BaseMessage"):
        make_method(handler, Req, request_stream=False)


def test_make_method_request_type_has_origin():
    from typing import List

    def handler(req: Req) -> Res:
        return Res()

    with pytest.raises(TypeError, match="Argument is not a type"):
        make_method(handler, List[Req], request_stream=False)


def test_check_request_consistency_with_none():
    with pytest.raises(TypeError, match="Argument type is None"):
        check_request_consistency(None, "func", "request")  # type: ignore


def test_check_request_consistency_with_non_type():
    with pytest.raises(TypeError, match="Argument is not a type"):
        check_request_consistency("not_a_type", "func", "request")  # type: ignore
