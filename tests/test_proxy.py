from pathlib import Path
from typing import Mapping, Sequence

import pytest

from makeproto.proxy import Message, bind_proxy, import_py_files_from_folder


class ProxyID(Message): ...


class ProxyUser(Message): ...


class ProxyCode(Message): ...


def test_convert(
    id: type,
    prodarea: type,
    enum2: type,
    code: type,
    product: type,
    user: type,
    requisition: type,
) -> None:

    p = Path(__file__).parent / "proto" / "compiled"

    modules = import_py_files_from_folder(p)

    bind_proxy(id, modules, ProxyID)
    bind_proxy(user, modules, ProxyUser)
    bind_proxy(code, modules, ProxyCode)
    # bind_proxy(Product, modules)
    # bind_proxy(Requisition, modules)

    # ID Tests
    n = 15
    proxy_id = ProxyID(id=n)
    assert proxy_id.id == n
    proto_id = proxy_id.unwrap()
    assert proto_id.id == n
    proxy_id2 = ProxyID(_proto_proxy=proto_id)
    assert proxy_id2.id == n

    n = 13
    proxy_id.id = n
    assert proxy_id.id == n
    proto_id = proxy_id.unwrap()
    assert proto_id.id == n
    proxy_id2 = ProxyID(_proto_proxy=proto_id)
    assert proxy_id2.id == n

    n = 12
    proto_id.id = n

    assert proxy_id.id == n
    proto_id = proxy_id.unwrap()
    assert proto_id.id == n
    proxy_id2 = ProxyID(_proto_proxy=proto_id)
    assert proxy_id2.id == n

    n = 11
    proxy_id2.id = n

    assert proxy_id.id == n
    proto_id = proxy_id.unwrap()
    assert proto_id.id == n
    proxy_id2 = ProxyID(_proto_proxy=proto_id)
    assert proxy_id2.id == n

    # Enum Tests

    obj_prodarea = prodarea.Area1
    obj_enum2 = enum2.e1

    # Code Tests

    code_num = 12
    s = ["foo", "bar"]
    le = [obj_prodarea]
    me = {"foo": obj_enum2}

    proxy_code = ProxyCode(code=code_num, pa=obj_prodarea, s=s, le=le, me=me)
    assert proxy_code.code == code_num
    assert proxy_code.pa == obj_prodarea
    assert proxy_code.s == s
    assert proxy_code.le == le
    assert proxy_code.me == me

    proto_code = proxy_code.unwrap()
    assert proto_code.code == code_num
    assert proto_code.pa == obj_prodarea.value
    assert proto_code.s == s
    assert proto_code.le == [l.value for l in le]
    assert proto_code.me == {k: v.value for k, v in me.items()}

    proxy_code2 = ProxyCode(_proto_proxy=proto_code)
    assert proxy_code2.code == code_num
    assert proxy_code2.pa == obj_prodarea
    assert proxy_code2.s == s
    assert proxy_code2.le == le
    assert proxy_code2.me == me

    assert proxy_code == proxy_code2

    # enum
    proxy_code.pa = prodarea.Area2
    assert proxy_code.pa == prodarea.Area2
    assert proto_code.pa == prodarea.Area2.value
    assert proxy_code2.pa == prodarea.Area2

    # list

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

    proxy_code.s = []
    assert proxy_code.s == []
    assert proto_code.s == []
    assert proxy_code2.s == []

    assert isinstance(proxy_code.s, Sequence)

    # unwrap
    proto1 = proxy_code.unwrap()
    proto2 = proxy_code2.unwrap()
    assert proto1 is proto2
    # dict

    assert proto_code.me["foo"] == enum2.e1.value

    assert "foo" in proxy_code.me
    del proxy_code.me["foo"]
    assert "foo" not in proxy_code.me

    assert proxy_code.me == {}
    assert proto_code.me == {}

    proxy_code.me["abc"] = enum2.e2
    assert proxy_code.me["abc"] == enum2.e2
    assert proto_code.me["abc"] == enum2.e2.value

    looped = False
    for k, v in proxy_code.me.items():
        looped = True
        assert isinstance(k, str)
        assert isinstance(v, enum2)
    assert looped

    proxy_code.me["123"] = enum2.e1
    assert proxy_code.me["123"] == enum2.e1
    assert proto_code.me["123"] == enum2.e1.value

    dictkeys = proxy_code.me.keys()
    assert dictkeys == ["abc", "123"]

    dictvalues = proxy_code.me.values()
    assert dictvalues == [enum2.e2, enum2.e1]

    dictitems = proxy_code.me.items()
    assert dictitems == [("abc", enum2.e2), ("123", enum2.e1)]

    assert proxy_code.me.get("abc") == enum2.e2
    assert proxy_code.me.get("nonexistent_key") is None

    assert proxy_code.me.pop("abc") == enum2.e2
    assert "abc" not in proxy_code.me
    assert proxy_code.me.get("abc") is None

    proxy_code.me.clear()
    assert proxy_code.me == {}
    assert proto_code.me == {}

    proxy_code.me.update({"new_key": enum2.e1})
    assert "new_key" in proxy_code.me
    assert proxy_code.me["new_key"] == enum2.e1

    default_value = enum2.e2
    assert proxy_code.me.setdefault("new_key", default_value) == enum2.e1
    assert proxy_code.me.get("new_key") == enum2.e1

    assert proxy_code.me.get("no_existant", None) is None
    assert proxy_code.me.get("no_existant", 45) == 45

    assert len(proxy_code.me) == 1
    proxy_code.me.set("new_key2", enum2.e1)
    assert len(proxy_code.me) == 2

    assert isinstance(proxy_code.me, Mapping)

    # assign wrong types
    with pytest.raises(TypeError):
        ProxyCode(code="not an int")

    with pytest.raises(AttributeError):
        proxy_code.pa = "not an enum"

    # AttributeError
    # proxy_code = ProxyCode(
    # code=code_num, pa=obj_prodarea, s=s, le=le, me={"foo": "bar"}
    # )
    # proxy_code.me["hello"] = "world"


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
