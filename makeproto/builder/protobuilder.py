from collections import defaultdict
from dataclasses import dataclass, field, fields
from typing import Optional, Sequence

from makeproto.prototypes import BaseMessage, BaseProto, Enum


@dataclass
class ProtoFile:
    imports: set[str] = field(default_factory=set[str])
    package: Optional[str] = None
    messages: set[type[BaseMessage]] = field(default_factory=set[type[BaseMessage]])


@dataclass
class ProtoBuilder:

    protofiles: dict[str, ProtoFile] = field(default_factory=dict)

    # tem que checar os packages, como namespace

    def add_message(self, msgtype: type[BaseMessage]):
        file_name = msgtype.__proto_file__
        if file_name not in self.protofiles:
            self.protofiles[file_name] = ProtoFile()
        self.protofiles[file_name].messages.add(msgtype)
        return file_name

    def map_messages(self, msgtype: type[BaseMessage]):
        if not isinstance(msgtype, type) or not issubclass(msgtype, BaseMessage):
            raise ValueError("XXX")

        file_name = self.add_message(msgtype)

        for field in fields(msgtype):
            if issubclass(field.type, BaseMessage):
                fname = field.type.__proto_file__
                if (
                    fname != file_name
                    and fname not in self.protofiles[file_name].imports
                ):
                    self.protofiles[file_name].imports.add(fname)
                self.map_messages(field.type)


def chain_class_dependants(
    cls: type[BaseMessage],
) -> tuple[Sequence[BaseMessage], Sequence[Enum]]: ...
