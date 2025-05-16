from enum import Enum
from typing import List

from makeproto.exceptions import ProtoBlockError
from makeproto.protoobj.base import FieldSpec, ProtoOption
from makeproto.protoobj.message import BaseMessage, get_headers
from makeproto.protoobj.rules import check_field_spec
from makeproto.template_models import Block, Field


def make_enumblock(
    enum: type[BaseMessage], default_protofile: str, default_package: str
) -> Block:

    exceptions: List[Exception] = []

    if not isinstance(enum, type) or not issubclass(enum, Enum):
        err = TypeError(
            f'Class "{enum.__name__}" is not an Enum, on make_enumblock function'
        )
        exceptions.append(err)

    fields: List[Field] = []

    for member in enum:
        name, value = member.name, member.value
        if not isinstance(value, int) or value < 0:
            err = TypeError(f"Enum Values should be positive int only. got {value}")
            exceptions.append(err)
        fields.append(
            Field(
                name=name, number=value, ftype=None, comment="", options=ProtoOption()
            )
        )

    protofile, package, comment, options, reserved = get_headers(
        enum, default_protofile, default_package
    )

    block_spec = FieldSpec(comment=comment, options=options)
    spec_exceptions = check_field_spec(block_spec, enum.__name__)
    exceptions.extend(spec_exceptions)

    if exceptions:
        raise ProtoBlockError(enum.__name__, "Enum", exceptions)

    enumBlock: Block = Block(
        protofile=protofile,
        package=package,
        name=enum.__name__,
        block_type="enum",
        fields=fields,
        comment=comment,
        options=options,
        reserved=reserved,
    )
    return enumBlock
