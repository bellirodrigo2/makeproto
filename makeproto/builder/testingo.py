

from dataclasses import MISSING, dataclass, field, fields, Field
from typing import Annotated, get_args, get_origin
from makeproto.builder.msgbuilder import MessageBuilder
from makeproto.prototypes import BaseField, BaseMessage, BaseProto, String



def make_message(msgtype:type):
    builder = MessageBuilder(msgtype.__name__)
    for field in fields(msgtype):
        builder.add_field(field)
    return builder.build()


def get_default(field):
    if field.default is not MISSING:
        return type(field.default)
    elif field.default_factory is not MISSING:
        type_ = type(field.default_factory)
        if type_ == type:
            return None
        return type_
    else:
        return None

def process_annotated(arg)->str:
    main_type = arg[0]
    extras = arg[1:]

def get_default_type(type_):
    if type_ == str:
        return 'string'

    
def get_type(field_type:type[BaseMessage])->str:

    origin = get_origin(field_type)
    args = get_args(field_type)
    
    
    if origin is Annotated:
        return process_annotated(args)


    # inner1:Inner
    if issubclass(field_type, BaseMessage):
        return field_type.__class__.__name__
    
    
    # str4:str = String()
    # str5:String = String()
    # str6:str = field(default='')
    default = get_default(field_type)
    if default is not None:
        return get_type(default)


    # str2:String
    # str7:String = field(default_factory=String)
    if issubclass(field_type, BaseField):
        return field_type.prototype()
    
    
    # str1:str
    default_type = get_default_type(field_type)
    if default_type:
        return default_type

def map_field(field:Field):
    ftype = field.type
    if issubclass(ftype, BaseField):
        basetype =ftype.python_type
        prototype = ftype
        collections = None
    if issubclass(ftype, BaseMessage):
        basetype = ftype
        prototype =  ftype
        collections = None
        
    origin = get_origin(ftype)
    args = get_args(field_type)
    
    if origin is Annotated:
        return get_type(args[0])

    if origin in {list, set, tuple}:
        return f'repeated {get_type(args[0])}'
    

@dataclass
class Inner(BaseMessage):
    ...
@dataclass
class FieldType:
    basetype: type
    prototype:type[BaseProto]
    collections: type[dict|list|set|tuple] | None

def get_field(field:dataclass.Field)

@dataclass
class User(BaseMessage):

    inner1:Inner
    inner2:Annotated[Inner, 'descriptor']
    inner3 = list[Inner]
    
    lstr1:list[str]
    lstr2:list[String]
    lstr3:Annotated[list[str], String()]
    
    str1:str
    str2:String
    str3:Annotated[str, String()]
    str4:str = String()
    str5:String = String()
    str6:str = field(default='')
    str7:String = field(default_factory=String)
    
    lstr4:list[str] = field(default_factory=list[str])
    lstr5:list[String] = field(default_factory=list[str])

    # if origin in {list, set, tuple}:
    #     return f'repeated {get_type(args[0])}'

    # if origin is dict:
    #     key_type, value_type = args
    #     return f"map<{get_type(key_type)}, {get_type(value_type)}>"

    # raise TypeError('XXX')
for field in fields(User):
    print(field.name, get_default(field))