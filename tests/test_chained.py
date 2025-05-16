from enum import Enum
from typing import Set

from makeproto.makeblock import cls_map, cls_to_blocks
from makeproto.protoobj.message import BaseMessage


def test_chanied(
    id: type[BaseMessage],
    prodarea: type[Enum],
    user: type[BaseMessage],
    code: type[BaseMessage],
    product: type[BaseMessage],
    enum2: type[Enum],
    requisition: type[BaseMessage],
) -> None:

    blocks = cls_to_blocks(requisition)

    block_names = [block.name for block in blocks]
    assert id.__name__ in block_names
    assert prodarea.__name__ in block_names
    assert user.__name__ in block_names
    assert code.__name__ in block_names
    assert product.__name__ in block_names
    assert enum2.__name__ in block_names
    assert requisition.__name__ in block_names
    assert len(block_names) == 7

    msgs: Set[BaseMessage] = cls_map(
        tgt=requisition, default_protofile="", default_package=""
    )

    msg_names = [msg.__name__ for msg in msgs]
    assert id.__name__ in msg_names
    assert prodarea.__name__ in msg_names
    assert user.__name__ in msg_names
    assert code.__name__ in msg_names
    assert product.__name__ in msg_names
    assert enum2.__name__ in msg_names
    assert requisition.__name__ in msg_names
    assert len(msg_names) == 7
