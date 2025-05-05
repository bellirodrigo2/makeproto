from typing import Annotated, get_origin

from makeproto.prototypes import OneOf


def teste_():
    OneOf[str]
    dd = Annotated[OneOf[str], 123]

    get_origin(dd)
