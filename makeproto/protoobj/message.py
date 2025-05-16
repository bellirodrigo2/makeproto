from typing import Any, List, Optional, Tuple, Union

from makeproto.protoobj.base import BaseProto, ProtoOption


class BaseMessage(BaseProto):

    @classmethod
    def prototype(cls) -> str:
        return cls.__name__

    @classmethod
    def qualified_prototype(cls) -> str:
        return f"{cls.package()}.{cls.__name__}"

    @classmethod
    def protofile(cls) -> str:
        raise NotImplementedError(
            f"protofile() must be implemented by the subclass. Not Found for: {cls.__name__}"
        )

    @classmethod
    def package(cls) -> str:
        return ""

    @classmethod
    def comment(cls) -> str:
        return ""

    @classmethod
    def options(cls) -> ProtoOption:
        return ProtoOption()

    @classmethod
    def reserved_index(cls) -> List[Union[int, range, str]]:
        return []


# ---------------- Extract Class Info ---------------------------------------


def get_module(
    cls: type[BaseMessage],
) -> Tuple[Optional[str], Optional[str]]:
    protofile_method = getattr(cls, "protofile", None)
    protofile: Optional[str] = None if protofile_method is None else protofile_method()

    package_method = getattr(cls, "package", None)
    package: Optional[str] = None if package_method is None else package_method()

    return protofile, package


def get_comment_options(
    cls: type[BaseMessage],
) -> Tuple[str, ProtoOption]:
    comment_method = getattr(cls, "comment", None)
    comment: str = "" if comment_method is None else comment_method()

    options_method = getattr(cls, "options", None)
    options: ProtoOption = ProtoOption() if options_method is None else options_method()

    return comment, options


def get_headers(
    cls: type[BaseMessage], default_protofile: str, default_package: str
) -> Tuple[Optional[str], Optional[str], str, ProtoOption, List[Any]]:

    protofile, package = get_module(cls)
    if protofile is None:
        protofile = default_protofile
    if package is None:
        package = default_package

    comment, options = get_comment_options(cls)

    reserved_method = getattr(cls, "reserved_index", None)
    reserved: List[Union[int, range]] = (
        [] if reserved_method is None else reserved_method()
    )
    return protofile, package, comment, options, reserved
