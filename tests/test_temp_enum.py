from makeproto.makemsg import make_enum_proto_str
from makeproto.prototypes import Enum


class MyEnum(Enum):
    VALID = 0
    INVALID = 1


class Enum2(Enum):
    FOO = 0
    BAR = 1


def test_msg_template():

    MYENUM2 = make_enum_proto_str(MyEnum)
    assert MYENUM2.startswith("enum MyEnum {")
    assert "VALID = 0;" in MYENUM2
    assert "INVALID = 1;" in MYENUM2
    assert MYENUM2.endswith("}")

    ENUM2 = make_enum_proto_str(Enum2)
    assert ENUM2.startswith("enum Enum2 {")
    assert "FOO = 0;" in ENUM2
    assert "BAR = 1;" in ENUM2
    assert ENUM2.endswith("}")
