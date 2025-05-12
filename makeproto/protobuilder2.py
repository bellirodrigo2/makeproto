from dataclasses import dataclass, field
from typing import Any, List, Optional, Set

from makeproto.makemsg2 import cls_to_blocks
from makeproto.models2 import Block, ProtoBlocks
from makeproto.prototypes2 import ProtoOption


@dataclass
class ProtoBlocksBuilder:
    pf: ProtoBlocks

    def add(self, new_block: Block) -> None:
        for existing in self.pf.blocks:
            if existing.name == new_block.name:
                if existing != new_block:
                    raise ValueError(
                        f"""Conflicting block "{new_block.name}" found in :
                        file "{self.pf.protofile}, package "{self.pf.package}"
                        with differing content.\nExisting: {existing}\nNew: {new_block}"""
                    )
                return  # Already exists and is identical — no-op
        self.pf.blocks.add(new_block)


@dataclass
class Protobuilder:

    packs: dict[str, ProtoBlocksBuilder] = field(default_factory=dict)
    files: dict[str, ProtoBlocksBuilder] = field(default_factory=dict)

    def _create_builder(
        self, protofile: str, package: Optional[str]
    ) -> ProtoBlocksBuilder:
        pf = ProtoBlocks(
            protofile=protofile,
            package=package,
            comment="",
            options=ProtoOption(),
        )
        return ProtoBlocksBuilder(pf)

    def get_protoblock(
        self, protofile: str, package: Optional[str]
    ) -> ProtoBlocksBuilder:
        existing_packages = {
            pack
            for pack, builder in self.packs.items()
            for block in builder.pf
            if block.protofile == protofile
        }

        def err_msg(existing_pack: str, new_package: str) -> str:
            return f"""Protofile "{protofile}" already exists in package: {existing_pack},
                    and cant be registered for package "{new_package}"."""

        if package:
            if existing_packages and (existing_packages != {package}):
                raise ValueError(err_msg(str(existing_packages), package))
            if protofile in self.files:
                raise ValueError(err_msg("NOPACKAGE", package))
        else:
            if existing_packages:
                raise ValueError(err_msg(str(existing_packages), "NOPACKAGE"))

        container, key = (self.packs, package) if package else (self.files, protofile)
        builder = container.get(key, None)
        if builder is None:
            builder = self._create_builder(protofile, package)
            container[key] = builder

        return builder

    def add_service(self, service: Block) -> None:

        protoblocks = self.get_protoblock(service.protofile, service.package)
        protoblocks.add(service)

        requests: List[type[Any]] = [m.request_type for m in service.fields]
        responses: List[type[Any]] = [m.response_type for m in service.fields]

        classes: set[type[Any]] = set(requests) | set(responses)

        blocks: set[Block] = set()
        for cls in classes:
            msgs = cls_to_blocks(cls)
            blocks.update(msgs)

        for block in blocks:
            msgblocks = self.get_protoblock(block.protofile, block.package)
            msgblocks.add(block)
