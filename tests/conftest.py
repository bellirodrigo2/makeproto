
from dataclasses import dataclass
import pytest
from makeproto.prototypes import BaseMessage, Float, Int32, String


@dataclass
class User(BaseMessage):
    __proto_file__ = "file.proto"  # apenas atributo da classe
    id: Int32
    name: String
    email:String
    tags:list[String]
    
@dataclass
class Product(BaseMessage):
    __proto_file__ = "file.proto"
    name:String
    unit_price: dict[String, Float]

@dataclass
class Requisition(BaseMessage):
    __proto_file__ = "file.proto"
    user:User
    product:Product
    quantity: Int32
    
@pytest.fixture
def msgs():
    return User, Product, Requisition
