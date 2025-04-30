from dataclasses import asdict, dataclass, fields
from typing import Mapping, get_origin

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
    def validate_types(self):
        for f in fields(self):
            value = getattr(self, f.name)
            exp = f.type
            origin = get_origin(exp)
            if origin is list:
                if not isinstance(value, list):
                    raise TypeError(
                        f"Field '{f.name}' expected a list, got {type(value)}"
                    )
            else:
                if not isinstance(value, exp):
                    raise TypeError(
                        f"Field '{f.name}' expected {exp}, got {type(value)}"
                    )

    def build(self):
        self.validate_types()
        template = env.from_string(self.__class__.msg)
        input = asdict(self)
        return template.render(template=input)


@dataclass
class ListObjTemplate(BaseTemplate):

    def validate_types(self):
        super().validate_types()
        allowed_keys = self.__class__.listkeys
        for el in [asdict(el) for el in self.listed]:
            if set(el.keys()) != set(allowed_keys):
                raise TypeError(
                    f'{self.__class__.__name__} should have keys in "{allowed_keys}" only'
                )


stdfield_str = """
        {{ template.type }} {{ template.name }} = {{ template.number }};
    """


@dataclass
class StdFieldTemplate(BaseTemplate):
    type: str
    name: str
    number: int

    msg = stdfield_str


enum_str = """
    enum {{ template.name }} {
          {% for enum in template.listed %}
          {{ enum.key }} = {{ enum.number }};
          {% endfor %}
        }
    """
# {{template.name}} {{template.key}} = {{template.number}}


@dataclass
class KeyNumber(BaseTemplate):
    key: str
    number: int


@dataclass
class EnumTemplate(ListObjTemplate):
    name: str
    listed: list[KeyNumber]

    msg = enum_str
    listkeys = ("key", "number")

    def validate_types(self):
        super().validate_types()
        for el in self.listed:
            if not isinstance(el.number, int) or not isinstance(el.key, str):
                raise TypeError(
                    f"Enum should have one int as values. Found {type(el.number)}"
                )


oneof_str = """
        oneof {{ template.name }} {
          {% for field in template.listed %}
          {{ field.type }} {{ field.name }} = {{ field.number }};
          {% endfor %}
        }
    """


@dataclass
class OneOfTemplate(ListObjTemplate):
    name: str
    listed: list[StdFieldTemplate]

    msg = oneof_str
    listkeys = ("type", "name", "number")


message_str2 = """
        message {{ template.name }} {
          {% for field in template.fields %}
          {{ field }}
          {% endfor %}
        }
    """


@dataclass
class MessageTemplate(BaseTemplate):
    name: str
    fields: list[str]

    msg = message_str2

    def validate_types(self):
        super().validate_types()
        for el in self.fields:
            if not isinstance(el, str):
                raise TypeError(
                    f'Fields should be "str" in MessageTemplate. A {type(el)} was encountered.'
                )


message_str = """
        message {{ message.name }} {
          {% for field in message.fields %}
          {{ field.type }} {{ field.name }} = {{ field.number }};
          {% endfor %}
        }
    """

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

message_template = env.from_string(message_str)

protofile_template = env.from_string(protofile_str)
