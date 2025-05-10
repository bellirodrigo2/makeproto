from dataclasses import dataclass, field
from typing import Any, Dict, Union

from makeproto.exceptions import (
    InconsistentPackageNameError,
)
from makeproto.makemsg import cls_to_blocks
from makeproto.models import EnumBlock, Field, MessageBlock, Method, ProtoFile, ServiceBlock
from makeproto.prototypes import BaseMessage, Enum
from makeproto.templates import render_protofile



@dataclass
class ProtoFileBuilder:
    pf: ProtoFile

    def __iter__(self):
        return iter(self.pf.blocks)

    def _find_block(self, name:str, block_type:str):
        for block in self.pf.blocks:
            if block.name == name and block.block_type == block_type:
                return block

    def add_block(self, tgt: Union[MessageBlock, ServiceBlock, EnumBlock]) -> None:

        btype = tgt.block_type
        tgtname = tgt.name

        if btype not in {"enum", "message", "service"}:
            raise ValueError(
                f'Block "{tgtname}" has an inconsistent "block_type": {btype}'
            )

        # tem que ser igual....pensar se vale a pena se um deles for None, adotar o outro
        if self.pf.package != tgt.package:
            raise InconsistentPackageNameError(
                self.pf.protofile,
                self.pf.package or "NOTDEFINED",
                tgt.package or "NOTDEFINED",
                tgt.name,
            )
        self.pf.blocks.add(tgt)
        
def get_obj(field:Field)->Union[BaseMessage, Enum, None]:
    ...

@dataclass
class Protobuilder:

    files: dict[str, ProtoFileBuilder] = field(default_factory=dict)

    def add_service(self, service: ServiceBlock):

        thisprotofile = self.files.get(service.name, None)

        if thisprotofile is None:
            pf = ProtoFile.make(protofile_name=service.protofile, package_name=service.package)
            builder = ProtoFileBuilder(pf)
            self.files[service.protofile] = builder
            thisprotofile = builder
            
        thisprotofile.add_block(service)

        requests = [m.request_type for m in service.fields]
        responses = [m.response_type for m in service.fields]

        classes: set[type[Any]] = set(requests) | set(responses)

        blocks:set[Union[MessageBlock, EnumBlock]] = set()
        for cls in classes:
            msgs = cls_to_blocks(cls)
            blocks.update(msgs)
        
        for block in blocks:

            msg_protofile = self.files.get(block.protofile)

            if msg_protofile is None:
                pf = ProtoFile.make(protofile_name=block.protofile, package_name=block.package)
                builder = ProtoFileBuilder(pf)
                self.files[block.protofile] = builder
                msg_protofile = builder

            msg_protofile.add_block(block)

    def _normalize(self)->None:
        
        for protofile in self.files.values():
            for block in protofile:
                for field in block:

                    if isinstance(field, Method):
                        if not field.request_type in protofile:
                            ...
                        if not field.response_type in protofile:
                            ...
                    elif isinstance(field, Field):
                        obj = get_obj(field)
                        if not obj in protofile:
                            ...
                    else:
                        raise

    def render(self) -> Dict[str,str]:

        self._normalize()

        rendered: Dict[str, str] = {}

        for filename, file in self.files.items():
            proto_str = render_protofile(file.pf)
            rendered[filename] = proto_str  
        return rendered

class SafeProtobuilder(Protobuilder):
    
    def render(self) -> Dict[str,str]:

        # checar consistencia entre protofiles e packages novamente.
        # checar consistencia entre os index... reserved
        # checar validate_name e snake_case

        # transformar names de packages diferentes...
        # checar ordem de aparecimento no file
        # checar imports

        # fazer interface para transformacoes e checagens

        # RAisE uma lista de erros....try/except cada
        return super().render()
