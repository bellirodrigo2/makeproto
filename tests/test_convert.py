from pathlib import Path

import tests.proto.compiled.teste_pb2 as proto
from makeproto.convert import to_proto
from makeproto.makemsg import make_enum_proto_str, make_message_proto_str
from makeproto.prototypes import BaseMessage, Enum
from scripts.compile_proto import compile
from tests.conftest import ProductArea


def test_compile_cls(
    id: type[BaseMessage],
    prodarea: type[Enum],
    user: type[BaseMessage],
    code: type[BaseMessage],
    product: type[BaseMessage],
    enum2: type[Enum],
    requisition: type[BaseMessage],
):

    msg_id = make_message_proto_str(id)
    # print(msg_id)
    msg_code = make_message_proto_str(code)
    # print(msg_code)
    msg_user = make_message_proto_str(user)
    # print(msg_user)
    msg_prodarea = make_enum_proto_str(prodarea)
    # print(msg_prodarea)
    msg_enum2 = make_enum_proto_str(enum2)
    # print(msg_enum2)
    msg_product = make_message_proto_str(product)
    # print(msg_product)
    msg_req = make_message_proto_str(requisition)
    # print(msg_req)

    protofile = f'syntax= "proto3";\n{msg_id}\n{msg_code}\n{msg_user}\n{msg_prodarea}\n{msg_enum2}\n{msg_product}\n{msg_req}\n'
    # print(protofile)

    folder = Path(__file__).parent / "proto"
    fname = "teste.proto"
    file = folder / fname
    with open(file, "w", encoding="utf-8") as f:
        f.write(protofile)
    assert compile(folder, fname, folder / "compiled")


def test_convert(
    id: type[BaseMessage],
    prodarea: type[ProductArea],
    enum2: type[Enum],
    code: type[BaseMessage],
    product: type[BaseMessage],
    user: type[BaseMessage],
    requisition: type[BaseMessage],
):

    n = 15
    obj_id = id(id=n)
    proto_id = to_proto(obj_id, proto.ID)
    assert obj_id.id == n
    assert proto_id.id == n

    obj_prodarea = prodarea.Area1
    obj_enum2 = enum2.e1

    code_num = 12
    obj_code = code(code=code_num, pa=obj_prodarea)
    proto_code = to_proto(obj_code, proto.Code)
    assert obj_code.code == code_num
    assert proto_code.code == code_num

    name = "John"
    unit_price = {"foo": 3.1415}
    obj_prod = product(
        name=name,
        unit_price=unit_price,
        code=obj_code,
        area=obj_prodarea,
        enum2=obj_enum2,
    )
    to_proto(obj_prod, proto.Product)

    name_user = "Maria"
    lastname = "Silva"
    email = "foo.bar@gmail.com"
    age = 49
    tags = ["foo", "bar"]
    oobool = True
    obj_user = user(
        id=obj_id,
        name=name_user,
        lastname=lastname,
        email=email,
        age=age,
        tags=tags,
        code2=obj_code,
        pa=obj_prodarea,
        o1=oobool,
        o2=None,
        o3=None,
        o4=None,
    )
    proto_user = to_proto(obj_user, proto.User)
    assert proto_user.id.id == obj_id.id
    assert proto_user.name == name_user

    assert proto_user.o1 == oobool
    assert proto_user.o2  == ''
    assert proto_user.o3  == 0
    assert proto_user.o4 == ''
    
    # obj_req = requisition(user=obj_u)
