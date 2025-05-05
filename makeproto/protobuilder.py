from dataclasses import dataclass, field, fields
from typing import Annotated, Any, Optional, get_args, get_origin

from makeproto.prototypes import BaseMessage, Enum


@dataclass
class ProtoFile:
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
