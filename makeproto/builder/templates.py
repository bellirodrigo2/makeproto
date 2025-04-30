from dataclasses import asdict, dataclass, fields
from typing import Any, get_args, get_origin, get_type_hints

from jinja2 import Environment

env = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
)


class BaseTemplate_:
    msg: str
    listkeys: tuple[str, ...] = ()


@dataclass
class BaseTemplate(BaseTemplate_):
    def __post_init__(self):
        type_hints = get_type_hints(self.__class__)
        for field in fields(self):
            name = field.name
            expected_type = type_hints.get(name, None)
            value = getattr(self, name)
            if expected_type is not None and not self._is_instance_of_type(
                value, expected_type
            ):
                raise TypeError(
                    f"Field '{name}' expected {expected_type}, got {type(value)} with value {value}"
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

    def build(self):
        template = env.from_string(self.__class__.msg)
        input = asdict(self)
        return template.render(template=input).strip()


stdfield_str = """
{{ template.type }} {{ template.name }} = {{ template.number }};
    """


@dataclass
class StdFieldTemplate(BaseTemplate):
    type: str
    name: str
    number: int

    msg = stdfield_str


    def set_number(self, num:int):
        self.number = num
        return num+1

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


    def set_number(self, num:int):
        
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

    {% for import in imports %}
    import "{{ import }}";
    {% endfor %}

    package {{ package }};

    {% for message in messages %}
    {{ message }}
    {% endfor %}
"""
