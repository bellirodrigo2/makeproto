from typing import Annotated, get_args, get_origin

from makeproto.prototypes import OneOf


def teste_():
    ct = OneOf[str]
    dd = Annotated[OneOf[str], 123]

    odd = get_origin(dd)
