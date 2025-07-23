# from dataclasses import dataclass
# from typing import Sequence


# @dataclass
# class MetaData:
#     name: str
#     options: Sequence[str]
#     comments: Sequence[str]


# @dataclass
# class APIModule(MetaData):

#     def make_service(
#         self, module_name: str, options: Sequence[str], comments: Sequence[str]
#     ) -> APIService:
#         pass


# @dataclass
# class APIPackage(MetaData):

#     def make_module(
#         self, module_name: str, options: Sequence[str], comments: Sequence[str]
#     ) -> APIModule:
#         pass
