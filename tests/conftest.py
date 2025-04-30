from dataclasses import dataclass
from typing import Annotated

import pytest

from makeproto.prototypes import BaseMessage, Float, Int32, OneOf, OneOfKey, String


@dataclass
class User(BaseMessage):
    __proto_file__ = "file.proto"  # apenas atributo da classe
    id: Int32
    name: String
    lastname: str
    email: String
    age: int
    tags: list[String]

    o1: Annotated[OneOf[bool], OneOfKey("oo1")]
    o2: OneOf[str] = OneOfKey("oo1")
    o3: OneOf[int] = OneOfKey("oo1")
    o4: OneOf[str] = OneOfKey("oo1")


@dataclass
class Product(BaseMessage):
    __proto_file__ = "file.proto"
    name: String
    unit_price: dict[String, Float]


@dataclass
class Requisition(BaseMessage):
    __proto_file__ = "file.proto"
    user: User
    product: Product
    quantity: Int32


@pytest.fixture
def msgs():
    return User, Product, Requisition
