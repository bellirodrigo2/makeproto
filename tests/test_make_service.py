from dataclasses import dataclass

from makeproto.makeservice import FuncSignature, make_service_proto_str
from makeproto.prototypes import BaseMessage


@dataclass
class Req1(BaseMessage): ...


@dataclass
class Req2(BaseMessage): ...


@dataclass
class Resp1(BaseMessage): ...


@dataclass
class Resp2(BaseMessage): ...


def test_service():

    funcs = [
        FuncSignature("method1", Req1, Resp1, False, False),
        FuncSignature("method2", Req2, Resp2, True, False),
        FuncSignature("method3", Req1, Resp1, False, True),
        FuncSignature("method4", Req2, Resp2, True, True),
    ]

    service = make_service_proto_str("Servive1", funcs)
    # print(service)
