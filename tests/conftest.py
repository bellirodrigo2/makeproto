from dataclasses import dataclass
from typing import Annotated

import pytest

from makeproto.prototypes import BaseMessage, Enum, Float, Int32, OneOf, OneOfKey, String

@dataclass
class ID(BaseMessage):
    id:int

@dataclass
class User(BaseMessage):
    __proto_file__ = "file.proto"  # apenas atributo da classe
    id: ID
    name: String
    lastname: str
    email: String
    age: int
    tags: list[String]
    code2:'Code'
    pa:'ProductArea'


    o1: Annotated[OneOf[bool], OneOfKey("oo1")]
    o2: OneOf[str] = OneOfKey("oo1")
    o3: OneOf[int] = OneOfKey("oo1")
    o4: OneOf[str] = OneOfKey("oo1")

@dataclass
class Code(BaseMessage):
    code:int
    code2:'Code'
    pa:'ProductArea'

class ProductArea(Enum):
    Area1=0
    Area2=1
    Area3=2

class Enum2(Enum):
    e1=0
    e2=1

@dataclass
class Product(BaseMessage):
    __proto_file__ = "file.proto"
    name: String
    unit_price: dict[String, Float]
    code:Code
    area:ProductArea
    enum2:Enum2


@dataclass
class Requisition(BaseMessage):
    __proto_file__ = "file.proto"
    user: User
    code:Code
    product: Product
    quantity: Int32
    enum2:Enum2


@pytest.fixture
def requisition():
    return Requisition
