from dataclasses import dataclass, field
from logging import warning
from typing import Any, Generic, Optional, TypeVar, Union

from makeproto.exceptions import (
    DuplicatedServiceNameError,
    InconsistentPackageNameError,
)
from makeproto.models import EnumBlock, MessageBlock, ServiceBlock


@dataclass
class ProtoModule:
    protofile_name: str
    package_name: Optional[str]

    def __post_init__(self):
        self.protofile_name = f'{self.protofile_name.rstrip(".proto")}.proto'


T = TypeVar("T")


@dataclass
class GBlock(ProtoModule, Generic[T]):
    block: T


Service = GBlock[ServiceBlock]
Message = GBlock[MessageBlock]
EnumMessage = GBlock[EnumBlock]


@dataclass
class ProtoFile(ProtoModule):

    imports: list[str] = field(default_factory=list)
    options: list[str] = field(default_factory=list)

    services: dict[str, Service] = field(default_factory=dict)
    messages: dict[str, Message] = field(default_factory=dict)
    enums: dict[str, EnumMessage] = field(default_factory=dict)

    def add_message(self, message: Message): ...

    def add_service(self, service: Service):

        self._check_consistency(service)

    def _check_consistency(self, tgt: Union[Message, Service, EnumMessage]):

        blocktype = tgt.block.block_type
        if blocktype == "message":
            map = self.messages
        elif blocktype == "service":
            map = self.services
        elif blocktype == "enum":
            map = self.enums
        else:
            raise ValueError(
                f'Block "{tgt.block.name}" has an inconsistent "block_type": {blocktype}'
            )

        # tem que ser igual....pensar se vale a pena se um deles for None, adotar o outro
        if self.package_name != tgt.package_name:
            raise InconsistentPackageNameError(
                self.protofile_name,
                self.package_name or "NOTDEFINED",
                tgt.package_name or "NOTDEFINED",
                tgt.block.name,
            )
        else:
            # check if there is a service with same name
            tgtname = tgt.block.name
            thisblock = map.get(tgtname, None)
            if thisblock is not None:
                # if there is and is different raise...
                if thisblock != tgt:
                    raise DuplicatedServiceNameError(tgtname, tgt.protofile_name)
                else:
                    # warning if trying to add same service twice
                    warning(f"Service {tgtname} is trying to be added twice")
                    ...
            else:
                map[tgtname] = tgt


@dataclass
class Protobuilder:

    files: dict[str, ProtoFile] = field(default_factory=dict)

    def add_message(self, message: Message): ...

    def add_service(self, service: Service):

        servblock = service.block
        protofile = self.files.get(servblock.name, None)

        if protofile is not None:
            protofile.add_service(service)
        else:
            pf = ProtoFile(service.protofile_name, service.package_name)
            pf.services[servblock.name] = service
            self.files[service.protofile_name] = pf

        requests = [m.request_type for m in service.block.fields]
        responses = [m.response_type for m in service.block.fields]

        classes: set[type[Any]] = set(requests) | set(responses)

        for cls in classes:
            ...

    def render(self) -> str:

        # checar consistencia entre protofiles e packages novamente.
        # checar consistencia entre os index... reserved
        # checar validate_name e snake_case

        # transformar names de packages diferentes...
        # checar ordem de aparecimento no file
        # checar imports

        # fazer interface para transformacoes e checagens

        # RAisE uma lista de erros....try/except cada
        ...
