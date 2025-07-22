from makeproto.interface import ILabeledMethod, IMetaType, IProtoPackage, IService

__all__ = [
    "compile_service",
    "IService",
    "ILabeledMethod",
    "IMetaType",
    "IProtoPackage",
]

from makeproto.build_service import compile_service
