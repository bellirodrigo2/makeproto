import tests.proto.compiled.teste_pb2 as proto


def test_only() -> None:

    objid = proto.ID(id=10)

    code_num = 12

    obj_prodarea = proto.ProductArea.Area1
    obj_enum2 = proto.Enum2.e1

    s = ["foo", "bar"]
    le = [obj_prodarea]
    me = {"foo": obj_enum2}

    objcode = proto.Code(code=code_num, pa=obj_prodarea, s=s, le=le, me=me)

    name = "John"
    unit_price = {"foo": 3.1415}
    objprod = proto.Product(
        name=name,
        unit_price=unit_price,
        code=objcode,
        area=obj_prodarea,
        enum2=obj_enum2,
    )
