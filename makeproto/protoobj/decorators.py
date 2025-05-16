from typing import Dict, List, Optional, Union

from makeproto.protoobj.base import ProtoOption


class ProtoModule:
    def __init__(self, profile: str, package: str = ""):
        self.profile = profile
        self.package_name = package

    def __call__(self, cls: type) -> type:
        cls.protofile = classmethod(lambda cls_: self.profile)
        cls.package = classmethod(lambda cls_: self.package_name)
        cls.prototype = classmethod(lambda cls_: cls_.__name__)
        cls.qualified_prototype = classmethod(
            lambda cls_: f"{cls.package()}.{cls.__name__}"
        )

        cls.comment = classmethod(lambda cls_: "")
        cls.options = classmethod(lambda cls_: ProtoOption())
        cls.reserved = classmethod(lambda cls_: [])

        return cls


class ProtoHeader:
    def __init__(
        self,
        comment: str = "",
        options: Optional[Dict[str, Union[str, bool]]] = None,
        reserved: Optional[List[Union[int, range]]] = None,
    ):
        self.comment = comment
        self.options = ProtoOption(**(options or {}))
        self.reserved = reserved or []

    def __call__(self, cls: type) -> type:
        cls.comment = classmethod(lambda cls_: self.comment)
        cls.options = classmethod(lambda cls_: self.options)
        cls.reserved = classmethod(lambda cls_: self.reserved)
        return cls
