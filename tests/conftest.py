from dataclasses import dataclass
from enum import Enum
from typing import Annotated, List

import pytest

from makeproto.prototypes2 import BaseMessage, FieldSpec, Float, Int32, OneOf, String


class TesteMessage(BaseMessage):
    protofile = "teste"
    package = "pack1"


@dataclass
class ID(TesteMessage):
    id: int


@dataclass
class User(TesteMessage):
    id: ID
    name: String
    lastname: str
    email: Annotated[
        String, FieldSpec(comment="email comment", options={"json_name": "email_field"})
    ]
    age: int
    tags: list[String]
    code2: "Code"
    pa: "ProductArea"

    o1: Annotated[bool, OneOf("oo1")]
    o2: Annotated[str, OneOf("oo1")]
    o3: Annotated[int, OneOf("oo1")]
    o4: Annotated[str, OneOf("oo1")]


@dataclass
class Code(TesteMessage):
    code: int
    pa: "ProductArea"
    s: List[str]
    le: list["ProductArea"]
    me: dict[str, "Enum2"]


class ProductArea(TesteMessage, Enum):
    Area1 = 0
    Area2 = 1
    Area3 = 2


class Enum2(TesteMessage, Enum):
    e1 = 0
    e2 = 1


@dataclass
class Product(TesteMessage):
    name: String
    unit_price: dict[String, Float]
    code: Code
    area: ProductArea
    enum2: Enum2


@dataclass
class Requisition(TesteMessage):
    user: User
    code: Code
    product: Product
    quantity: Int32
    enum2: Enum2


@pytest.fixture
def user():
    return User


@pytest.fixture
def code():
    return Code


@pytest.fixture
def product():
    return Product


@pytest.fixture
def enum2():
    return Enum2


@pytest.fixture
def id():
    return ID


@pytest.fixture
def prodarea():
    return ProductArea


@pytest.fixture
def requisition():
    return Requisition
