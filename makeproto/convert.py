from dataclasses import asdict
from enum import Enum
from typing import Any, Optional, TypeVar

from makeproto.message import Message

T = TypeVar("T")


def convert_enums(map: dict[str, Any]) -> dict[str, Any]:

    resolved_args: dict[str, Any] = {}
    for k, v in map.items():
        if isinstance(v, Enum):
            resolved_args[k] = v.value
        elif isinstance(v, list) or isinstance(v, set):
            resolved_args[k] = [
                item.value if isinstance(item, Enum) else item for item in v
            ]
        elif isinstance(v, dict):
            resolved_args[k] = convert_enums(v)
        else:
            resolved_args[k] = v
    return resolved_args


def to_proto(obj: Message, prototype: type[T], case_mode: Optional[str] = None) -> T:

    # args = snake_keys(obj.to_dict())

    args = asdict(obj)
    resolved_args = convert_enums(args)
    return prototype(**resolved_args)


def from_proto(obj: T, bettertype: Message) -> Message:
    args = {field.name: getattr(obj, field.name) for field in obj.DESCRIPTOR.fields}
    return bettertype(**args)


# user =User(id=123, name='Rodrigo', email='rb@gmail.com', tags = ['foo','bar'])
# product = Product(name='bag', type='backpack', unit_price=149.9)

# requisition = Requisition(user=user, product=product, quantity=20)

# req_pb = to_proto(requisition, pb.Requisition)
# print(req_pb)

# req2 = from_proto(req_pb, Requisition)
# print(req2.user)
# print(req2.product)
# print(req2.quantity)
