from dataclasses import dataclass, field, fields
from logging import warning
from typing import Annotated, Any, Optional, get_args, get_origin

from makeproto.prototypes import BaseMessage, Enum
from makeproto.templates import EnumTemplate, MessageTemplate, ServiceTemplate


@dataclass
class ProtoModule:
    protofile_name: str
    package_name: Optional[str]

    def __post_init__(self):
        self.protofile_name = f'{self.protofile_name.rstrip(".proto")}.proto'


@dataclass
class Service(ProtoModule):
    service: ServiceTemplate


@dataclass
class Message(ProtoModule):
    msg: MessageTemplate


@dataclass
class EnumMessage(ProtoModule):
    msg: EnumTemplate


@dataclass
class ProtoFile(ProtoModule):

    imports: list[str] = field(default_factory=list)
    options: list[str] = field(default_factory=list)

    services: dict[str, Service] = field(default_factory=dict)
    messages: list[Message] = field(default_factory=list)
    enums: list[EnumMessage] = field(default_factory=list)


@dataclass
class Protobuilder:

    files: dict[str, ProtoFile] = field(default_factory=dict)

    def _map_messages(self, service: Service): ...

    def add_service(self, service: Service):

        serv_proto_name = service.protofile_name
        protofile = self.files.get(serv_proto_name, None)
        serv_name = service.service.name

        # there is a protofile with same name
        if protofile is not None:
            # check if package name is consistent
            if (
                protofile.package_name != service.package_name
            ):  # tem que ser igual....pensar se vale a pena se um for None, deixar ok
                raise Exception(
                    protofile.protofile_name,
                    protofile.package_name,
                    service.package_name,
                )
            else:
                # check if there is a service with same name
                services = protofile.services.get(serv_name, None)
                if services is not None:
                    # if there is and is different raise...
                    if services != service:
                        raise Exception
                    else:
                        # warning if trying to add same service twice
                        warning("")
                        ...
                else:
                    protofile.services[serv_name] = service
        else:
            self.files[serv_proto_name] = ProtoFile(
                protofile_name=serv_proto_name, package_name=service.package_name
            )

        # preciso extrair req e resp aqui from service
        # requests = [req for req in service.]


@dataclass
class ProtoFile2:
    imports: set[str] = field(default_factory=set[str])
    package: Optional[str] = None
    options: Optional[list[str]] = None
    messages: set[type[BaseMessage]] = field(default_factory=set[type[BaseMessage]])


def isbasemsg(msgtype: Any):
    return isinstance(msgtype, type) and issubclass(msgtype, BaseMessage)  # type: ignore


@dataclass
class ProtoBuilder:

    protofiles: dict[str, ProtoFile] = field(default_factory=dict)

    def add_message(self, msgtype: type[BaseMessage]):

        if not isbasemsg(msgtype):
            raise ValueError("XXX")

        self._add_imports(msgtype)

        file_name = msgtype.__proto_file__
        if file_name not in self.protofiles:
            self.protofiles[file_name] = ProtoFile()
        else:
            # checar se bate o package
            this_pckg = msgtype.__proto_package__
            existing_pckg = self.protofiles[file_name].package
            if this_pckg != existing_pckg:
                raise ValueError(
                    f'Protofile {file_name} already defined with package: "{existing_pckg}" and {this_pckg} passed for class "{msgtype.__name__}"'
                )

        self.protofiles[file_name].messages.add(msgtype)
        return file_name

    def _add_imports(self, msgtype: type[BaseMessage]):

        file_name = self.add_message(msgtype)

        for field in fields(msgtype):
            if isinstance(field.type, type) and issubclass(field.type, BaseMessage):
                fname = field.type.__proto_file__
                if (
                    fname != file_name
                    and fname not in self.protofiles[file_name].imports
                ):
                    self.protofiles[file_name].imports.add(fname)
                # self.map_messages(field.type)

    def add_option(self, protofile: str, options: Any): ...


def chain_dependants(msgtype: type[BaseMessage]) -> set[type[BaseMessage]]:

    if not isbasemsg(msgtype):
        raise ValueError("XXX")

    bm = set([msgtype])

    for field in fields(msgtype):

        ftype = field.type
        if get_origin(ftype) is Annotated:
            ftype = get_args(ftype)[0]

        if isbasemsg(ftype):
            bm.add(ftype)
            if not issubclass(ftype, Enum):
                dependants = chain_dependants(ftype)
            bm.update(dependants)
    return bm
