

from typing import Annotated, get_args, get_origin


d = dict[str,int]
d2 = Annotated[dict[str,int], 'hello']

def get_type(field_type)->str:
    
    origin = get_origin(field_type)
    print(origin)    
    return ''

get_type(d)