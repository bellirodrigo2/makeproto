from dataclasses import dataclass
from typing import Annotated

from makeproto.message import define_oneof_fields
import pytest

from enum import Enum as StdEnum
from makeproto.prototypes import (
    BaseMessage,
    Enum,
    FieldOptions,
    Float,
    Int32,
    OneOf,
    OneOfKey,
    String,
)

class TesteMessage(BaseMessage):
    __proto_file__ = 'teste'

@dataclass
class ID(TesteMessage):
    id: int


@dataclass
class User(TesteMessage):
    id: ID
    name: String
    lastname: str
    email: Annotated[
        String, FieldOptions(comments="email comment", json_name="email_field")
    ]
    age: int
    tags: list[String]
    code2: "Code"
    pa: "ProductArea"

    o1: Annotated[OneOf[bool], OneOfKey("oo1")]
    o2: Annotated[OneOf[str], OneOfKey("oo1")]
    o3: Annotated[OneOf[int], OneOfKey("oo1")]
    o4: Annotated[OneOf[str], OneOfKey("oo1")]


@dataclass
class Code(TesteMessage):
    code: int
    pa: "ProductArea"
    s: set[str]
    le: list["ProductArea"]
    me: dict[str, "Enum2"]


class ProductArea(Enum):
    Area1 = 0
    Area2 = 1
    Area3 = 2


class Enum2(StdEnum):
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


define_oneof_fields(ID)
define_oneof_fields(User)
define_oneof_fields(Code)
define_oneof_fields(Product)
define_oneof_fields(Requisition)


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
