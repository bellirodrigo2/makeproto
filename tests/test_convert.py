from enum import Enum
from pathlib import Path

from makeproto.makeblock import make_msgblock
from makeproto.makeenum import make_enumblock
from makeproto.protoobj.message import BaseMessage
from makeproto.template_render import render_block


def test_compile_cls(
    id: type[BaseMessage],
    prodarea: type[Enum],
    user: type[BaseMessage],
    code: type[BaseMessage],
    product: type[BaseMessage],
    enum2: type[Enum],
    requisition: type[BaseMessage],
) -> None:

    msg_id_block = make_msgblock(id, "", "")
    msg_id = render_block(msg_id_block)
    # print(msg_id)
    msg_code_block = make_msgblock(code, "", "")
    msg_code = render_block(msg_code_block)
    # print(msg_code)
    msg_block_user = make_msgblock(user, "", "")
    msg_user = render_block(msg_block_user)
    # print(msg_user)
    msg_block_prodarea = make_enumblock(prodarea, "", "")
    msg_prodarea = render_block(msg_block_prodarea)
    # print(msg_prodarea)
    msg_enum2_block = make_enumblock(enum2, "", "")
    msg_enum2 = render_block(msg_enum2_block)
    # print(msg_enum2)
    msg_block_product = make_msgblock(product, "", "")
    msg_product = render_block(msg_block_product)
    # print(msg_product)
    msg__block_req = make_msgblock(requisition, "", "")
    msg_req = render_block(msg__block_req)
    # print(msg_req)

    protofile = f'syntax= "proto3";\n{msg_prodarea}\n{msg_enum2}\n{msg_id}\n{msg_code}\n{msg_user}\n{msg_product}\n{msg_req}\n'
    # print(protofile)

    folder = Path(__file__).parent / "proto"
    fname = "teste2.proto"
    file = folder / fname
    with open(file, "w", encoding="utf-8") as f:
        f.write(protofile)
    # assert compile(folder, fname, folder / "compiled")
