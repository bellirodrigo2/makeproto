from pathlib import Path

from makeproto.makemsg import make_enumblock, make_msgblock
from makeproto.prototypes import BaseMessage, Enum
from makeproto.templates import render_block
from scripts.compile_proto import compile


def test_compile_cls(
    id: type[BaseMessage],
    prodarea: type[Enum],
    user: type[BaseMessage],
    code: type[BaseMessage],
    product: type[BaseMessage],
    enum2: type[Enum],
    requisition: type[BaseMessage],
):

    msg_id_block = make_msgblock(id)
    msg_id = render_block(msg_id_block)
    # print(msg_id)
    msg_code_block = make_msgblock(code)
    msg_code = render_block(msg_code_block)
    # print(msg_code)
    msg_block_user = make_msgblock(user)
    msg_user = render_block(msg_block_user)
    # print(msg_user)
    msg_block_prodarea = make_enumblock(prodarea)
    msg_prodarea = render_block(msg_block_prodarea)
    # print(msg_prodarea)
    msg_enum2_block = make_enumblock(enum2)
    msg_enum2 = render_block(msg_enum2_block)
    # print(msg_enum2)
    msg_block_product = make_msgblock(product)
    msg_product = render_block(msg_block_product)
    # print(msg_product)
    msg__block_req = make_msgblock(requisition)
    msg_req = render_block(msg__block_req)
    # print(msg_req)

    protofile = f'syntax= "proto3";\n{msg_prodarea}\n{msg_enum2}\n{msg_id}\n{msg_code}\n{msg_user}\n{msg_product}\n{msg_req}\n'
    # print(protofile)

    folder = Path(__file__).parent / "proto"
    fname = "teste.proto"
    file = folder / fname
    with open(file, "w", encoding="utf-8") as f:
        f.write(protofile)
    assert compile(folder, fname, folder / "compiled")


# def test_convert(
#     id: type[ID],
#     prodarea: type[ProductArea],
#     enum2: type[Enum2],
#     code: type[Code],
#     product: type[Product],
#     user: type[User],
#     requisition: type[Requisition],
# ):

#     p = Path(__file__).parent / "proto" / "compiled"

#     converter = Converter(p)

#     converter.define_needconvert_fields(ID)
#     converter.define_needconvert_fields(User)
#     converter.define_needconvert_fields(Code)
#     converter.define_needconvert_fields(Product)
#     converter.define_needconvert_fields(Requisition)

#     # ID Tests
#     n = 15
#     obj_id = id(id=n)
#     assert obj_id.id == n

#     proto_id = converter.to_proto(obj_id)
#     assert proto_id.id == n

#     cls_id = converter.from_proto(proto_id, id)
#     assert cls_id.id == obj_id.id

#     # Enum Tests

#     obj_prodarea = prodarea.Area1
#     obj_enum2 = enum2.e1

#     # Code Tests

#     code_num = 12
#     s = set(["foo", "bar"])
#     le = [obj_prodarea]
#     me = {"foo": obj_enum2}
#     obj_code = code(code=code_num, pa=obj_prodarea, s=s, le=le, me=me)

#     proto_code = converter.to_proto(obj_code)
#     assert proto_code.code == code_num
#     assert proto_code.pa == obj_prodarea.value
#     for item in proto_code.s:  # order is not garanteed
#         assert item in s
#     assert proto_code.le == [l.value for l in le]
#     assert proto_code.me == {k: v.value for k, v in me.items()}

#     cls_code = converter.from_proto(proto_code, code)
#     assert cls_code == obj_code
#     assert cls_code.pa == obj_code.pa
#     assert cls_code.s == obj_code.s
#     assert cls_code.le == obj_code.le
#     assert cls_code.me == obj_code.me

#     # PRoduct TEst

#     name = "John"
#     unit_price = {"foo": 3.1415}
#     obj_prod = product(
#         name=name,
#         unit_price=unit_price,
#         code=obj_code,
#         area=obj_prodarea,
#         enum2=obj_enum2,
#     )

#     proto_product = converter.to_proto(obj_prod)
#     assert proto_product.name == name

#     for k, v in proto_product.unit_price.items():
#         assert f"{v:.2f}" == f"{unit_price[k]:.2f}"

#     assert proto_product.code.code == obj_prod.code.code
#     assert proto_product.code.code == obj_prod.code.code
#     for item in proto_product.code.s:
#         assert item in obj_prod.code.s
#     assert proto_product.code.le == [l.value for l in obj_prod.code.le]
#     assert proto_product.code.me == {k: v.value for k, v in obj_prod.code.me.items()}

#     cls_product = converter.from_proto(proto_product, Product)
#     assert cls_product.name == name

#     for k, v in cls_product.unit_price.items():
#         assert f"{v:.2f}" == f"{unit_price[k]:.2f}"

#     assert cls_product.code.code == obj_prod.code.code
#     assert cls_product.code.code == obj_prod.code.code
#     assert cls_product.code.s == obj_prod.code.s
#     assert cls_product.code.le == obj_prod.code.le
#     assert cls_product.code.me == obj_prod.code.me

#     # User TEst

#     name_user = "Maria"
#     lastname = "Silva"
#     email = "foo.bar@gmail.com"
#     age = 49
#     tags = ["foo", "bar"]
#     oobool = True
#     obj_user = user(
#         id=obj_id,
#         name=name_user,
#         lastname=lastname,
#         email=email,
#         age=age,
#         tags=tags,
#         code2=obj_code,
#         pa=obj_prodarea,
#         o1=oobool,
#         o2=None,
#         o3=None,
#         o4=None,
#     )
#     proto_user = converter.to_proto(obj_user)
#     assert proto_user.id.id == obj_id.id
#     assert proto_user.name == name_user
#     assert proto_user.lastname == lastname
#     assert proto_user.email == email
#     assert proto_user.age == age
#     assert proto_user.tags == tags
#     assert proto_user.code2.pa == obj_code.pa.value

#     assert proto_user.o1 == oobool
#     assert proto_user.o2 == ""
#     assert proto_user.o3 == 0
#     assert proto_user.o4 == ""

#     cls_user = converter.from_proto(proto_user, user)
#     assert cls_user.id.id == obj_id.id
#     assert cls_user.name == name_user
#     assert cls_user.lastname == lastname
#     assert cls_user.email == email
#     assert cls_user.age == age
#     assert cls_user.tags == tags
#     assert cls_user.code2.pa == obj_code.pa

#     assert cls_user.o1 == oobool
#     assert cls_user.o2 == ""
#     assert cls_user.o3 == 0
#     assert cls_user.o4 == ""

#     # Requisition Test

#     quantity = 32
#     obj_req = requisition(
#         user=obj_user,
#         code=obj_code,
#         product=obj_prod,
#         quantity=quantity,
#         enum2=obj_enum2,
#     )

#     proto_req = converter.to_proto(obj_req)
#     assert proto_req.user.id.id == obj_user.id.id
#     assert proto_req.user.name == obj_user.name
#     assert proto_req.user.lastname == obj_user.lastname
#     assert proto_req.user.email == obj_user.email
#     assert proto_req.user.tags == obj_user.tags
#     assert proto_req.user.code2.code == obj_user.code2.code
#     assert proto_req.user.code2.pa == obj_user.code2.pa.value
#     for item in proto_req.user.code2.s:
#         assert item in obj_user.code2.s

#     assert proto_req.user.code2.le == [l.value for l in obj_user.code2.le]
#     assert proto_req.user.code2.me == {k: v.value for k, v in obj_user.code2.me.items()}

#     assert proto_req.user.pa == obj_user.pa.value
#     assert proto_req.user.o1 == obj_user.o1

#     assert not proto_req.user.o2 and not obj_user.o2
#     assert not proto_req.user.o3 and not obj_user.o3
#     assert not proto_req.user.o4 and not obj_user.o4

#     assert proto_req.enum2 == obj_enum2.value
#     assert proto_req.quantity == quantity

#     cls_req = converter.from_proto(proto_req, requisition)
#     assert cls_req.user.id.id == obj_user.id.id
#     assert cls_req.user.name == obj_user.name
#     assert cls_req.user.lastname == obj_user.lastname
#     assert cls_req.user.email == obj_user.email
#     assert cls_req.user.tags == obj_user.tags
#     assert cls_req.user.code2.code == obj_user.code2.code
#     assert cls_req.user.code2.pa == obj_user.code2.pa
#     for item in cls_req.user.code2.s:
#         assert item in obj_user.code2.s

#     assert cls_req.user.code2.le == obj_user.code2.le
#     assert cls_req.user.code2.me == obj_user.code2.me

#     assert cls_req.user.pa == obj_user.pa
#     assert cls_req.user.o1 == obj_user.o1

#     assert not cls_req.user.o2 and not obj_user.o2
#     assert not cls_req.user.o3 and not obj_user.o3
#     assert not cls_req.user.o4 and not obj_user.o4

#     assert cls_req.enum2 == obj_enum2
#     assert cls_req.quantity == quantity
