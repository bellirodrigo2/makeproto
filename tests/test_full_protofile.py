from typing import Optional

import pytest

from makeproto.protobuilder import ProtoBlocksBuilder, Protobuilder
from makeproto.protoobj.base import ProtoOption
from makeproto.template_models import Block


def make_block(
    protofile: str, package: Optional[str], name: str, block_type: str
) -> Block:
    return Block(
        protofile=protofile,
        package=package,
        name=name,
        block_type=block_type,
        fields=set(),
        comment="",
        options=ProtoOption(),
        reserved_index=[],
        reserved_keys="",
    )


@pytest.fixture
def builder() -> Protobuilder:
    return Protobuilder()


def test_get_protoblock_creates_in_files_when_no_package(builder: Protobuilder) -> None:
    blk = make_block("file.proto", None, "Msg", "message")
    pb = builder.get_protoblock(blk.protofile, blk.package)
    assert isinstance(pb, ProtoBlocksBuilder)
    assert "file.proto" in builder.files
    assert blk.package is None


def test_get_protoblock_creates_in_packs_when_with_package(
    builder: Protobuilder,
) -> None:
    blk = make_block("file.proto", "pkg", "Msg", "message")
    pb = builder.get_protoblock(blk.protofile, blk.package)
    assert isinstance(pb, ProtoBlocksBuilder)
    assert "pkg" in builder.packs
    assert blk.package == "pkg"


def test_get_protoblock_same_file_same_package_returns_same(
    builder: Protobuilder,
) -> None:
    blk1 = make_block("f.proto", "pkg", "A", "message")
    pb1 = builder.get_protoblock(blk1.protofile, blk1.package)
    blk2 = make_block("f.proto", "pkg", "B", "message")
    pb2 = builder.get_protoblock(blk2.protofile, blk2.package)
    assert pb1 is pb2


def test_get_protoblock_error_if_same_file_in_different_package(
    builder: Protobuilder,
) -> None:
    blk1 = make_block("f.proto", "pkg1", "A", "message")
    b1 = builder.get_protoblock(blk1.protofile, blk1.package)
    b1.add(blk1)
    blk2 = make_block("f.proto", "pkg2", "B", "message")
    with pytest.raises(ValueError):
        builder.get_protoblock(blk2.protofile, blk2.package)


def test_get_protoblock_error_if_file_in_files_then_with_package(
    builder: Protobuilder,
) -> None:
    blk1 = make_block("f.proto", None, "A", "message")
    builder.get_protoblock(blk1.protofile, blk1.package)
    blk2 = make_block("f.proto", "pkg", "B", "message")
    with pytest.raises(ValueError):
        builder.get_protoblock(blk2.protofile, blk2.package)


def test_get_protoblock_error_if_file_in_package_then_without(
    builder: Protobuilder,
) -> None:
    blk1 = make_block("f.proto", "pkg", "A", "message")
    b1 = builder.get_protoblock(blk1.protofile, blk1.package)
    b1.add(blk1)
    blk2 = make_block("f.proto", None, "B", "message")
    with pytest.raises(ValueError):
        builder.get_protoblock(blk2.protofile, blk2.package)


def test_add_service_adds_block(builder: Protobuilder) -> None:
    blk = make_block("file.proto", "pkg", "Svc", "service")
    builder.add_service(blk)
    pb = builder.packs["pkg"]
    # service added
    assert any(b.name == "Svc" for b in pb.pf.blocks)


def test_add_service_duplicate_no_error(builder: Protobuilder) -> None:
    blk = make_block("file.proto", "pkg", "Svc", "service")
    builder.add_service(blk)
    # add again should not raise
    builder.add_service(blk)
    pb = builder.packs["pkg"]
    assert len([b for b in pb.pf.blocks if b.name == "Svc"]) == 1


def test_add_service_conflict_in_add(builder: Protobuilder) -> None:
    blk1 = make_block("file.proto", None, "Svc", "service")
    blk2 = make_block("file.proto", None, "Svc", "service")
    # same signature; modify blk2 to conflict
    blk2.block_type = "message"
    builder.add_service(blk1)
    with pytest.raises(ValueError):
        builder.add_service(blk2)
