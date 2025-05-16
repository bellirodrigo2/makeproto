from makeproto.protoobj.decorators import ProtoHeader, ProtoModule

proto1 = ProtoModule("proto1", "pack1")


@proto1
class C1:
    pass


@ProtoHeader(comment="Custom header", reserved=["id"])
@proto1
class C2:
    pass


@ProtoHeader(comment="Custom header", options={"foo": "bar"})
class C3:
    pass


def test_decorators() -> None:

    assert C1.protofile() == "proto1"
    assert C1.package() == "pack1"
    assert C1.comment() == ""
    assert C1.reserved() == []

    assert C2.protofile() == "proto1"
    assert C2.package() == "pack1"
    assert C2.comment() == "Custom header"
    assert C2.reserved() == ["id"]

    assert C3.comment() == "Custom header"
    assert C3.reserved() == []
    assert C3.options() == {"foo": "bar"}
