from makeproto.makemsg import cls_to_blocks
from makeproto.prototypes import BaseMessage, Enum


def test_chanied(
    id: type[BaseMessage],
    prodarea: type[Enum],
    user: type[BaseMessage],
    code: type[BaseMessage],
    product: type[BaseMessage],
    enum2: type[Enum],
    requisition: type[BaseMessage],
):

    msgs = cls_to_blocks(requisition)

    msg_names = [msg.name for msg in msgs]
    assert id.__name__ in msg_names
    assert prodarea.__name__ in msg_names
    assert user.__name__ in msg_names
    assert code.__name__ in msg_names
    assert product.__name__ in msg_names
    assert enum2.__name__ in msg_names
    assert requisition.__name__ in msg_names
