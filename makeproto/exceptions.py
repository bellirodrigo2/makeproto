
from typing import Any


class NotConvertableClassError(Exception):...

class ConvertingError(Exception):

    def __init__(
        self,
        converting: str,
        clstype: str,
        field: str,
        value: Any,
        expected: str,
        cause: Exception,
    ):

        self.msg = f'Error when converting "{clstype}" {converting} proto. Field "{field}" has value "{value}" of type "{type(value)}", when "{expected}" was expected'
        self.__cause__ = cause
        super().__init__(self.msg)

class InconsistentPackageNameError(Exception):
    
    def __init__(self, protofile:str, package1:str, package2:str, tgt_service:str):
        ...


class DuplicatedServiceNameError(Exception):
    
    def __init__(self, servicename:str, protofile:str):
        ...