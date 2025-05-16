from enum import Enum
from typing import Annotated, List, Union

import pytest

from makeproto.protoobj.base import FieldSpec, OneOf
from makeproto.protoobj.message import BaseMessage
from makeproto.protoobj.types import Float, Int32, String


class TesteMessage(BaseMessage):
    @classmethod
    def protofile(cls) -> str:
        return "teste"

    @classmethod
    def package(cls) -> str:
        return "pack1"


class ID(TesteMessage):
    id: int


class User(TesteMessage):
    id: ID
    name: String
    lastname: str
    email: Annotated[
        String,
        FieldSpec(
            comment="email comment", options={"json_name": "email_field"}, index=20
        ),
    ]
    age: int
    tags: list[String] = FieldSpec(index=4)
    code2: "Code"
    pa: "ProductArea" = FieldSpec(index=7)

    o1: Annotated[bool, OneOf(key="oo1", index=3)]
    o2: Annotated[str, OneOf("oo1")]
    o3: Annotated[int, OneOf("oo1")]
    o4: Annotated[str, OneOf("oo1")]


class Code(TesteMessage):

    @classmethod
    def reserved(cls) -> List[Union[int, range]]:
        return [range(3, 18)]

    code: int
    pa: "ProductArea"
    s: List[str]
    le: list["ProductArea"]
    me: dict[str, "Enum2"] = FieldSpec(comment="dict[str,Enum2]", index=1)


class ProductArea(TesteMessage, Enum):
    Area1 = 0
    Area2 = 1
    Area3 = 2


class Enum2(TesteMessage, Enum):
    e1 = 0
    e2 = 1


class Product(TesteMessage):
    name: String
    unit_price: dict[String, Float]
    code: Code
    area: ProductArea
    enum2: Enum2


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
