from dataclasses import asdict, dataclass
from typing import Any, Optional, Union, get_args, get_origin

from jinja2 import Environment

from makeproto.mapclass import FuncArg, get_dataclass_fields

env = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
)


class BaseTemplate_:
    msg: str
    listkeys: tuple[str, ...] = ()


def check_optional(arg: FuncArg, value: Any) -> bool:
    args = arg.args
    if arg.origin is Union and type(None) in args:
        if value is None or type(value) in args:
            return True
        raise TypeError(
            f'Optional Field "{arg.name}" should have a value None or {arg.basetype}. Found {type(value)}'
        )
    return False


@dataclass
class BaseTemplate(BaseTemplate_):
    def __post_init__(self):

        args = get_dataclass_fields(self.__class__)

        for arg in args:
            name = arg.name
            value = getattr(self, name)
            if check_optional(arg, value):
                continue
            if arg.basetype is not None and not self._is_instance_of_type(
                value, arg.basetype
            ):
                raise TypeError(
                    f"Field '{name}' expected {arg.basetype}, got {type(value)} with value {value}"
                )

    def _is_instance_of_type(self, value: Any, expected_type: Any) -> bool:
        origin = get_origin(expected_type)
        args = get_args(expected_type)
        if origin is None:
            return isinstance(value, expected_type)
        elif origin is list:
            return isinstance(value, list) and all(
                self._is_instance_of_type(v, args[0]) for v in value
            )
        return False

    def set_number(self, num: int) -> int:
        return num

    def build(self) -> str:
        template = env.from_string(self.__class__.msg)
        input = asdict(self)
        return template.render(template=input).strip()


# stdfield_str = """
# {{ template.type }} {{ template.name }} = {{ template.number }};
# """
stdfield_str = """
{% if template.comments -%}
// {{ template.comments }}
{% endif -%}
{{ template.type }} {{ template.name }} = {{ template.number }}{% if template.json_name %} [json_name = "{{ template.json_name }}"]{% endif %};
"""


@dataclass
class StdFieldTemplate(BaseTemplate):
    type: str
    name: str
    number: int
    comments: Optional[str] = None
    json_name: Optional[str] = None

    msg = stdfield_str

    def set_number(self, num: int) -> int:
        self.number = num
        return num + 1


enum_str = """enum {{ template.name }} {
    {% for enum in template.listed %}
    {{ enum.key }} = {{ enum.number }};
    {% endfor %}
}"""


@dataclass
class KeyNumber(BaseTemplate):
    key: str
    number: int


@dataclass
class EnumTemplate(BaseTemplate):
    name: str
    listed: list[KeyNumber]

    msg = enum_str


oneof_str = """
oneof {{ template.name }} {
    {% for field in template.listed %}
    {{ field.type }} {{ field.name }} = {{ field.number }};
    {% endfor %}
}
    """


@dataclass
class OneOfTemplate(BaseTemplate):
    name: str
    listed: list[StdFieldTemplate]

    msg = oneof_str

    def set_number(self, num: int):

        for stdtemp in self.listed:
            num = stdtemp.set_number(num)
        return num


message_str = """message {{ template.name }} {
{% for field in template.fields %}
  {{ field }}
{% endfor %}
}"""


@dataclass
class MessageTemplate(BaseTemplate):
    name: str
    fields: list[str]

    msg = message_str


protofile_str = """
    syntax = "proto3";

    {% for import in template.imports %}
    import "{{ import }}";
    {% endfor %}

    package {{ template.package }};

    {% for message in template.messages %}
    {{ message }}
    {% endfor %}
"""
