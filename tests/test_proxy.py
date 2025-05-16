from enum import Enum
from pathlib import Path
from typing import Annotated, Dict, List, Mapping, Sequence, Tuple

import pytest

from makeproto.protoobj.base import FieldSpec, OneOf
from makeproto.protoobj.types import Float, String
from makeproto.proxy.importer import import_py_files_from_folder
from makeproto.proxy.proto_proxy import bind_proxy
from makeproto.proxy.proxy import ProxyMessage

# class ProtoMessage(ProxyMessage):
#     @classmethod
#     def protofile(cls) -> str:
#         return "teste"


# class ID(ProtoMessage):
#     id: int


# class User(ProtoMessage):
#     id: ID
#     name: String
#     lastname: str
#     email: Annotated[
#         String, FieldSpec(comment="email comment", options={"json_name": "email_field"})
#     ]
#     age: int
#     tags: list[String]
#     code2: "Code"
#     pa: "ProductArea"

#     o1: Annotated[bool, OneOf("oo1")]
#     o2: Annotated[str, OneOf("oo1")]
#     o3: Annotated[int, OneOf("oo1")]
#     o4: Annotated[str, OneOf("oo1")]


# class Code(ProtoMessage):
#     code: int
#     pa: "ProductArea"
#     s: List[str]
#     le: list["ProductArea"]
#     me: dict[str, "Enum2"]


# class ProductArea(Enum):
#     Area1 = 0
#     Area2 = 1
#     Area3 = 2


# class Enum2(Enum):
#     e1 = 0
#     e2 = 1


# class Product(ProtoMessage):
#     name: String
#     unit_price: dict[String, Float]
#     code: Code
#     area: ProductArea
#     enum2: Enum2


class ProtoMessage(ProxyMessage):
    @classmethod
    def protofile(cls) -> str:
        return "teste"


class ID(ProtoMessage):
    id: int


class User(ProtoMessage):
    id: ID
    name: String
    lastname: str
    email: Annotated[
        String,
        FieldSpec(comment="email comment", options={"json_name": "email_field"}),
    ]
    age: int
    tags: list[String]
    code2: "Code"
    pa: "ProductArea"
    o1: Annotated[bool, OneOf("oo1")]
    o2: Annotated[str, OneOf("oo1")]
    o3: Annotated[int, OneOf("oo1")]
    o4: Annotated[str, OneOf("oo1")]


class Code(ProtoMessage):
    code: int
    pa: "ProductArea"
    s: List[str]
    le: list["ProductArea"]
    me: dict[str, "Enum2"]


class ProductArea(Enum):
    Area1 = 0
    Area2 = 1
    Area3 = 2


class Enum2(Enum):
    e1 = 0
    e2 = 1


class Product(ProtoMessage):
    name: String
    unit_price: dict[String, Float]
    code: Code
    area: ProductArea
    enum2: Enum2


p = Path(__file__).parent / "proto" / "compiled"
modules = import_py_files_from_folder(p)
bind_proxy(ID, modules)
bind_proxy(User, modules)
bind_proxy(Code, modules)
bind_proxy(Product, modules)
# bind_proxy(Requisition, modules)


@pytest.fixture
def id() -> Tuple[ID, int]:
    n = 15
    proxy_id = ID(id=n)

    return proxy_id, n


@pytest.fixture
def code() -> (
    Tuple[Code, Enum, Enum, int, List[str], List[ProductArea], Dict[str, Enum2]]
):
    obj_prodarea = ProductArea.Area1
    obj_enum2 = Enum2.e1

    code_num = 12
    s = ["foo", "bar"]
    le = [obj_prodarea]
    me = {"foo": obj_enum2}

    return (
        Code(code=code_num, pa=obj_prodarea, s=s, le=le, me=me),
        obj_prodarea,
        obj_enum2,
        code_num,
        s,
        le,
        me,
    )


@pytest.fixture
def product(
    code: Tuple[Code, Enum, Enum, int, List[str], List[ProductArea], Dict[str, Enum2]],
) -> Product:

    proxy_code, obj_prodarea, obj_enum2, _, _, _, _ = code

    name = "John"
    unit_price = {"foo": 3.1415}

    return (
        Product(
            name=name,
            unit_price=unit_price,
            code=proxy_code,
            area=obj_prodarea,
            enum2=obj_enum2,
        ),
        proxy_code,
    )


def test_proxy(id: Tuple[ID, int]) -> None:
    proxy_id, n = id
    assert proxy_id.id == n
    proto_id = proxy_id.unwrap
    assert proto_id.id == n
    proxy_id2 = ID(_wrapped=proto_id)
    assert proxy_id2.id == n

    n = 13
    proxy_id.id = n
    assert proxy_id.id == n
    proto_id = proxy_id.unwrap
    assert proto_id.id == n
    proxy_id2 = ID(_wrapped=proto_id)
    assert proxy_id2.id == n

    n = 12
    proto_id.id = n

    assert proxy_id.id == n
    proto_id = proxy_id.unwrap
    assert proto_id.id == n
    proxy_id2 = ID(_wrapped=proto_id)
    assert proxy_id2.id == n

    n = 11
    proxy_id2.id = n

    assert proxy_id.id == n
    proto_id = proxy_id.unwrap
    assert proto_id.id == n
    proxy_id2 = ID(_wrapped=proto_id)
    assert proxy_id2.id == n


def test_code_simple(
    code: Tuple[Code, Enum, Enum, int, List[str], List[ProductArea], Dict[str, Enum2]],
) -> None:

    proxy_code, obj_prodarea, obj_enum2, code_num, s, le, me = code
    proto_code = proxy_code.unwrap
    proxy_code2 = Code(_wrapped=proto_code)

    assert proxy_code.code == code_num
    assert proxy_code.pa == obj_prodarea
    assert proxy_code.s == s
    assert proxy_code.le == le
    assert proxy_code.me == me

    assert proto_code.code == code_num
    assert proto_code.pa == obj_prodarea.value
    assert proto_code.s == s
    assert proto_code.le == [l.value for l in le]
    assert proto_code.me == {k: v.value for k, v in me.items()}

    assert proxy_code2.code == code_num
    assert proxy_code2.pa == obj_prodarea
    assert proxy_code2.s == s
    assert proxy_code2.le == le
    assert proxy_code2.me == me

    assert proxy_code == proxy_code2


def test_code_enum(
    code: Tuple[Code, Enum, Enum, int, List[str], List[ProductArea], Dict[str, Enum2]],
) -> None:

    proxy_code, _, _, _, _, _, _ = code
    proto_code = proxy_code.unwrap
    proxy_code2 = Code(_wrapped=proto_code)

    proxy_code.pa = ProductArea.Area2
    assert proxy_code.pa == ProductArea.Area2
    assert proto_code.pa == ProductArea.Area2.value
    assert proxy_code2.pa == ProductArea.Area2


def test_code_list(
    code: Tuple[Code, Enum, Enum, int, List[str], List[ProductArea], Dict[str, Enum2]],
) -> None:

    proxy_code, _, _, _, s, _, _ = code
    proto_code = proxy_code.unwrap
    proxy_code2 = Code(_wrapped=proto_code)

    proxy_code.s.append("hello")
    assert len(proxy_code.s) == 3
    assert len(proto_code.s) == 3
    assert len(proxy_code2.s) == 3
    for s in proxy_code2.s:
        assert isinstance(s, str)
    proto_code.s.append("world")
    assert len(proxy_code.s) == 4
    assert len(proto_code.s) == 4
    assert len(proxy_code2.s) == 4
    assert "world" in proxy_code2.s

    proxy_code.s = ["new"]
    assert proxy_code.s == ["new"]
    assert proto_code.s == ["new"]
    assert proxy_code2.s == ["new"]

    proxy_code.s[0] = "modified"
    assert proxy_code.s[0] == "modified"
    assert proto_code.s[0] == "modified"

    proxy_code.s.extend(["more", "values"])
    assert proxy_code.s[-2:] == ["more", "values"]

    proxy_code.s.insert(1, "middle")
    assert proxy_code.s[1] == "middle"

    proxy_code.s.remove("middle")
    assert "middle" not in proxy_code.s

    item = proxy_code.s.pop()
    assert item == "values"

    proxy_code.s.clear()
    assert proxy_code.s == []
    assert proto_code.s == []
    assert proxy_code2.s == []

    proxy_code.s = ["a", "b", "c"]
    proxy_code.s.reverse()
    assert proxy_code.s == ["c", "b", "a"]

    copy_list2 = proxy_code.s.copy()
    assert copy_list2 == ["c", "b", "a"]
    copy_list2.pop()
    assert len(copy_list2) == 2

    proxy_code.s = ["b", "c", "a"]
    proxy_code.s.sort()
    assert proxy_code.s == ["a", "b", "c"]

    copy_list = list(proxy_code.s)
    assert copy_list == ["a", "b", "c"]
    copy_list.pop()

    assert len(proxy_code.s) == 3

    proxy_code.s[:2] = ["x", "y"]
    assert proxy_code.s[:2] == ["x", "y"]


def test_code_dict(
    code: Tuple[Code, Enum, Enum, int, List[str], List[ProductArea], Dict[str, Enum2]],
) -> None:

    proxy_code, _, _, _, _, _, _ = code
    proto_code = proxy_code.unwrap

    assert proto_code.me["foo"] == Enum2.e1.value

    assert "foo" in proxy_code.me
    del proxy_code.me["foo"]
    assert "foo" not in proxy_code.me

    assert proxy_code.me == {}
    assert proto_code.me == {}

    proxy_code.me["abc"] = Enum2.e2
    assert proxy_code.me["abc"] == Enum2.e2
    assert proto_code.me["abc"] == Enum2.e2.value

    looped = False
    for k, v in proxy_code.me.items():
        looped = True
        assert isinstance(k, str)
        assert isinstance(v, Enum2)
    assert looped

    proxy_code.me["123"] = Enum2.e1
    assert proxy_code.me["123"] == Enum2.e1
    assert proto_code.me["123"] == Enum2.e1.value

    dictkeys = proxy_code.me.keys()
    assert list(dictkeys).sort() == ["abc", "123"].sort()

    dictvalues = proxy_code.me.values()
    for v in [Enum2.e2, Enum2.e1]:
        assert v in dictvalues

    dictitems = proxy_code.me.items()
    assert dictitems.sort() == [("abc", Enum2.e2), ("123", Enum2.e1)].sort()

    assert proxy_code.me.get("abc") == Enum2.e2
    assert proxy_code.me.get("nonexistent_key") is None

    assert proxy_code.me.pop("abc") == Enum2.e2
    assert "abc" not in proxy_code.me
    assert proxy_code.me.get("abc") is None

    proxy_code.me.clear()
    assert proxy_code.me == {}
    assert proto_code.me == {}

    proxy_code.me.update({"new_key": Enum2.e1})
    assert "new_key" in proxy_code.me
    assert proxy_code.me["new_key"] == Enum2.e1

    default_value = Enum2.e2
    assert proxy_code.me.setdefault("new_key", default_value) == Enum2.e1
    assert proxy_code.me.get("new_key") == Enum2.e1

    assert proxy_code.me.get("no_existant", None) is None
    assert proxy_code.me.get("no_existant", 45) == 45

    assert len(proxy_code.me) == 1
    proxy_code.me.set("new_key2", Enum2.e1)
    assert len(proxy_code.me) == 2

    with pytest.raises(TypeError, match="set method for key:"):
        proxy_code.me.set("new_key2", 0)

    with pytest.raises(TypeError, match=" to None on DictProxy"):
        proxy_code.me.set("new_key2", None)

    with pytest.raises(TypeError, match="set method for key:"):
        proxy_code.me["new_key2"] = 0

    with pytest.raises(TypeError, match=" to None on DictProxy"):
        proxy_code.me["new_key2"] = None

    assert isinstance(proxy_code.me, Mapping)


def test_code_unwrap(
    code: Tuple[Code, Enum, Enum, int, List[str], List[ProductArea], Dict[str, Enum2]],
) -> None:

    proxy_code, _, _, _, _, _, _ = code
    proto_code = proxy_code.unwrap
    proxy_code2 = Code(_wrapped=proto_code)

    # unwrap
    proto1 = proxy_code.unwrap
    proto2 = proxy_code2.unwrap
    assert proto1 is proto2


def test_code_wrong(
    code: Tuple[Code, Enum, Enum, int, List[str], List[ProductArea], Dict[str, Enum2]],
) -> None:

    proxy_code, obj_prodarea, obj_enum2, _, s, _, _ = code
    proto_code = proxy_code.unwrap
    proxy_code2 = Code(_wrapped=proto_code)

    proxy_code.s = []
    assert proxy_code.s == []
    assert proto_code.s == []
    assert proxy_code2.s == []

    proxy_code.s.append("foo")

    with pytest.raises(TypeError, match="At ListProxy set method for index:"):
        proxy_code.s[0] = 4
    with pytest.raises(TypeError, match="At ListProxy append method: Expected"):
        proxy_code.s.append(4)

    with pytest.raises(TypeError, match="At ListProxy extend method: Expected"):
        proxy_code.s.extend(4)

    assert isinstance(proxy_code.s, Sequence)

    # assign wrong types
    with pytest.raises(TypeError):
        Code(code="not an int")

    with pytest.raises(TypeError, match="set: Expected "):
        proxy_code.pa = "not an enum"

    with pytest.raises(TypeError, match="set: Expected "):
        proxy_code.code = "not an int"

    with pytest.raises(TypeError, match="set: Expected "):
        proxy_code.s = 3

    with pytest.raises(TypeError, match="set: Expected "):
        proxy_code.me = 3

    #     # PRoduct TEst


def test_product(product: Product) -> None:

    proxy_product, proxy_code = product

    assert proxy_product.code == proxy_code
    assert proxy_product.code.code == proxy_code.code


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

#     assert proto_req.enum2 == obj_Enum2.value
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
