import dataclasses
from typing import Annotated, Any, get_args, get_origin

from dataclasses import asdict, dataclass, field, fields

from makeproto.builder.jinja_templates import message_template
from makeproto.prototypes import BaseField, BaseProto, Bool, Bytes, Float, Int64, String

@dataclass
class MessageBuilder:
    name:str
    fields:list[dict[str,str|int]] = field(default_factory=list)

    def add_field(self, field_type:dataclasses.Field):
        name = field_type.name
        type_str = get_type(field_type.type)
        counter = len(self.fields)
        
        msgfield = {'name': name, 'type': type_str, 'number': counter}
        self.fields.append(msgfield)

    def build(self):
        template = message_template
        return template.render(message=asdict(self))


def get_default(field_type:type[BaseProto])->str:
    
    bclass:type[BaseField] | None = None
    if issubclass(field_type, int):
        bclass = Int64
    if issubclass(field_type, float):
        bclass = Float
    if issubclass(field_type, str):
        bclass = String
    if issubclass(field_type, bytes):
        bclass = Bytes
    if issubclass(field_type, bool):
        bclass = Bool
    if bclass is not None:
        return bclass.prototype()
    raise TypeError()
    
    

def get_type(field_type:type[BaseProto])->str:
    
    if issubclass(field_type, BaseProto):
        return field_type.prototype()
    
    origin = get_origin(field_type)
    args = get_args(field_type)
    
    if origin is Annotated:
        return get_type(args[0])

    if origin in {list, set, tuple}:
        return f'repeated {get_type(args[0])}'

    if origin is dict:
        key_type, value_type = args
        return f"map<{get_type(key_type)}, {get_type(value_type)}>"

    return get_default(field_type)

def make_message(msgtype:type):
    builder = MessageBuilder(msgtype.__name__)
    for field in fields(msgtype):
        builder.add_field(field)
    return builder.build()
        
    