from collections import defaultdict
from enum import Enum
from typing import Dict, List, Optional, Set, Union

from makeproto.exceptions import ProtoBlockError
from makeproto.indexer import Indexer
from makeproto.makeenum import make_enumblock
from makeproto.mapclass import map_class_fields
from makeproto.protoobj.base import FieldSpec, OneOf, ProtoOption
from makeproto.protoobj.message import BaseMessage, get_headers, get_module
from makeproto.protoobj.rules import check_arg, check_field_spec
from makeproto.template_models import Block, Field


def validate_field_indexes(
    field_indexes: Dict[str, int], indexer: Indexer
) -> List[Exception]:

    exceptions: List[Exception] = []

    def is_in_index_range(number: int) -> bool:
        return 1 <= number <= 536870911

    for name, index in field_indexes.items():

        if not isinstance(index, int):  # type: ignore
            err = TypeError(f'Field "{name}" has a non integer index: "{index}"')
            exceptions.append(err)
            continue

        if index in indexer:
            exceptions.append(
                ValueError(
                    f'Field "{name}" has an index of: "{index}" which is reserved'
                )
            )
        same_index = [idx for idx in field_indexes.values() if idx == index]
        if len(same_index) > 1:
            exceptions.append(
                ValueError(f'Field "{name}" has a duplicated index of: "{index}"')
            )
        if not is_in_index_range(index):
            exceptions.append(
                ValueError(
                    f'Field "{name}" has an index of: "{index}" which is out of range (from 0 to 536870911)'
                )
            )

    return exceptions


def resolve_indexes(block: Block, indexer: Indexer) -> None:

    for item in block:
        if isinstance(item, Field):
            if item.number == 0:
                item.number = indexer.next
        elif isinstance(item, Block):
            resolve_indexes(item, indexer)


def sort_block(block: Block) -> None:
    block.fields.sort(key=lambda x: x.number)


def make_msgblock(
    cls: type[BaseMessage], default_protofile: str, default_package: str
) -> Block:

    args = map_class_fields(cls, False)

    exceptions: List[Exception] = []

    protofile, package, comment, options, reserved = get_headers(
        cls, default_protofile, default_package
    )

    block_spec = FieldSpec(comment=comment, options=options)
    spec_exceptions = check_field_spec(block_spec, cls.__name__)
    exceptions.extend(spec_exceptions)

    field_indexes: Dict[str, int] = {}

    fields: List[Block] = []
    oneofs: Dict[str, List[Field]] = defaultdict(list)

    for arg in args:

        exception = check_arg(arg)
        if exception is not None:
            exceptions.append(exception)
            continue

        spec = arg.getinstance(FieldSpec, True)
        if spec is not None:
            spec_exceptions = check_field_spec(spec, arg.name)
            exceptions.extend(spec_exceptions)
        fcomment = spec.comment if spec is not None else ""
        foptions = spec.options if spec is not None else ProtoOption()
        findex = spec.index if spec is not None else 0

        if findex != 0:
            field_indexes[arg.name] = findex

        field = Field(
            name=arg.name,
            ftype=arg.basetype,
            comment=fcomment,
            options=foptions,
            number=findex,
        )

        if spec is not None and isinstance(spec, OneOf):
            key = spec.key
            oneofs[key].append(field)
        else:
            fields.append(field)

    for k, v in oneofs.items():
        # como pegar options e comments em nivel de block ?
        ootemp = Block(
            protofile=protofile,
            package=package,
            name=k,
            block_type="oneof",
            fields=v,
            comment="",
            options=ProtoOption(),
            reserved=str([]),
        )
        fields.append(ootemp)

    indexer = Indexer(idxs=reserved)
    indexer.reserve(range(1900, 1999))  # reserved by google

    index_exceptions = validate_field_indexes(field_indexes, indexer)
    exceptions.extend(index_exceptions)

    if exceptions:
        raise ProtoBlockError(cls.__name__, "class", exceptions)

    block = Block(
        protofile=protofile,
        package=package,
        name=cls.__name__,
        block_type="message",
        fields=fields,
        comment=comment,
        options=options,
        reserved=str(Indexer(idxs=reserved)),
    )

    for idx in field_indexes.values():
        indexer.reserve(idx)

    resolve_indexes(block, indexer)
    sort_block(block)
    return block


def cls_map(
    tgt: type[BaseMessage],
    default_protofile: str,
    default_package: str,
    visited: Optional[Set[Block]] = None,
) -> Set[BaseMessage]:

    if not isinstance(tgt, type):  # type: ignore
        raise TypeError(f'tgt argumento should be a type. found "{tgt}"')

    if visited is None:
        visited: Set[BaseMessage] = set()

    # Evita regenerar blocos que já foram criados
    if any(b.__name__ == tgt.__name__ for b in visited):
        return visited

    if issubclass(tgt, Enum) or issubclass(tgt, BaseMessage):
        visited.add(tgt)

        args = map_class_fields(tgt, False)

        for arg in args:
            bt = arg.basetype
            if arg.istype(BaseMessage):
                protofile, package = get_module(bt)
                msgs = cls_map(
                    arg.basetype,
                    protofile or default_protofile,
                    package or default_package,
                    visited,
                )
                visited.update(msgs)

    return visited


def cls_to_blocks(
    tgt: type[BaseMessage],
) -> List[Block]:

    defproto = tgt.protofile()
    defpack = tgt.package()
    clss = cls_map(tgt, defproto, defpack)

    blocks: List[Block] = []
    for cls in clss:
        if issubclass(cls, Enum):
            enumblock = make_enumblock(cls, defproto, defpack)
            blocks.append(enumblock)
        elif issubclass(cls, BaseMessage):
            msgblock = make_msgblock(cls, defproto, defpack)
            blocks.append(msgblock)
    return blocks


# def OLDcls_to_blocks(
#     tgt: type[BaseMessage],
#     default_protofile: str,
#     default_package: str,
#     visited: Optional[set[Block]] = None,
# ) -> set[Block]:

#     if not isinstance(tgt, type):  # type: ignore
#         raise TypeError(f'tgt argumento should be a type. found "{tgt}"')

#     if visited is None:
#         visited: Set[Block] = set()

#     # Evita regenerar blocos que já foram criados
#     if any(b.name == tgt.__name__ for b in visited):
#         return visited

#     if issubclass(tgt, Enum):
#         enumblock = make_enumblock(tgt, default_protofile, default_package)
#         visited.add(enumblock)

#     elif issubclass(tgt, BaseMessage):  # type: ignore
#         msgblock = make_msgblock(tgt, default_protofile, default_package)
#         visited.add(msgblock)

#         args = map_class_fields(tgt, False)

#         for arg in args:
#             bt = arg.basetype
#             if arg.istype(BaseMessage):
#                 protofile, package = get_module(bt)
#                 msgs = cls_to_blocks(
#                     arg.basetype,
#                     protofile or default_protofile,
#                     package or default_package,
#                     visited,
#                 )
#                 visited.update(msgs)

#     return visited
