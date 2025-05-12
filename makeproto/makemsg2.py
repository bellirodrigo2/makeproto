from collections import defaultdict
from typing import Any, List, Union
from makeproto.mapclass import FuncArg, get_dataclass_fields
from makeproto.models import Block2, Field2, MessageBlock, OneOfBlock
from makeproto.prototypes2 import BaseMessage, BaseProto,DEFAULT_PRIMITIVES, FieldSpec, OneOf, ProtoOption,allowed_map_key

def check_type(bt:type[Any], arg_name:str, cls_name:str):
     
    if not isinstance(bt, type):  # type: ignore
        return TypeError(f'On class "{cls_name}", field "{arg_name}" is not a type. Found {bt}')

    if issubclass(bt, BaseProto):  # type: ignore
        return None

    if bt not in DEFAULT_PRIMITIVES:
        return TypeError(f'On class "{cls_name}", field "{arg_name}" type is not allowed. Found {bt}')
    
    return None


def check_arg(arg:FuncArg, cls_name:str):
    
    if arg.basetype is None:
            return TypeError(f'Field "{arg.name}" in class "{cls_name}" has no type Annotation')
    
    bt = arg.basetype
    origin = arg.origin
    args = arg.args

    if origin in {list, set}:
        return check_type(args[0], arg.name, cls_name)

    if origin is dict:
        if args[0] in allowed_map_key:
            return check_type(args[1], arg.name, cls_name)
        return TypeError(f'Field "{arg.name}" in class "{cls_name}" is a dict with not allowed key type. Found "{args[0]}" as dict key')

    return check_type(bt, arg.name, cls_name)


def make_msgblock(cls: type[BaseMessage]) -> MessageBlock:

    args = get_dataclass_fields(cls, False)
    #fazer get_class_fields (sem ser dataclass)

    fields: list[Union[Field2, Block2[Field2]]] = []
    oneofs: dict[str, list[Field2]] = defaultdict(list)
    
    exceptions:List[Exception] = []

    for arg in args:

        exception = check_arg(arg, cls.__name__)
        if exception is not None:
             exceptions.append(exception)
             continue
        comment = ''
        options = ProtoOption()
        index = 0

        spec = arg.getinstance(FieldSpec)
        if spec is not None:
            comment = spec.comment
            options = spec.options
            index = spec.index

        field = Field2(name=arg.name,ftype=arg.basetype,comment=comment, options=options,number=index)

        if isinstance(spec, OneOf):
            key = spec.key
            oneofs[key].append(field)
        else:
            fields.append(field)

    protofile = cls.protofile
    package = cls.package  
    comment = cls.comment
    options = cls.options
    reserved = cls.reserved

    for k, v in oneofs.items():
        #como pegar options e comments em nivel de block ?
        ootemp = Block2(
            protofile=protofile,
            package=package,
            name=k,
            block_type="oneof",
            fields=v,
            comment='',
            options={},
            reserved=[]
        )
        fields.append(ootemp)

    block = Block2(
        protofile=protofile,
        package=package,
        name=cls.__name__,
        block_type="message",
        fields=fields,
        comment=comment,
        options=options,
        reserved=reserved
    )

    if exceptions:
        raise CustomExceptions(exceptions)

    return block
