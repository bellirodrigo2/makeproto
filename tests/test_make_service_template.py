from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from makeproto.interface import ILabeledMethod, IService
from makeproto.make_service_template import make_service_template


@dataclass
class LabeledMethod(ILabeledMethod):
    name: str = field(default="")
    method: Callable[..., Any] = field(default=lambda x: x)
    module: str = field(default="module1")
    service: str = field(default="service1")
    package: str = field(default="")
    options: Sequence[str] = field(default_factory=list[str])
    comments: str = field(default="")
    request_types: Sequence[Any] = field(default_factory=list[Any])
    response_types: Optional[Any] = None


@dataclass
class Service(IService):
    name: str = field(default="service1")
    module: str = field(default="module1")
    package: str = ""
    options: Sequence[str] = field(default_factory=list[str])
    comments: str = ""
    _methods: Sequence[LabeledMethod] = field(default_factory=list[LabeledMethod])

    @property
    def methods(self) -> Sequence[LabeledMethod]:
        return self._methods

    @property
    def qual_name(self) -> str:
        if self.package:
            return f"{self.package}.{self.name}"
        return self.name


def test_no_method() -> None:

    service = Service()
    temp = make_service_template(service)

    assert temp.name == "service1"
    assert temp.methods == []


def test_no_method() -> None:

    method = LabeledMethod()
    service = Service(_methods=[method])
    temp = make_service_template(service)

    assert temp.name == "service1"
    method_temp = temp.methods[0]
    assert method_temp.name == method.name
    assert method_temp.method_func == method.method
