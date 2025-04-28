
from dataclasses import dataclass, field, fields
from inspect import isclass

from makeproto.basefield import BaseField
from makeproto.basemessage import BaseMessage, User


@dataclass
class ProtoBuilder:

    messages:list[type[BaseMessage]]=field(default_factory=list)

    def add_message(self, msg:type[BaseMessage])->None:

        for field in fields(msg):
            if issubclass(field.type, BaseField):
                print(field)

builder = ProtoBuilder()

builder.add_message(User)