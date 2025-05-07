from dataclasses import asdict, dataclass, field
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
        elif origin is dict:
            if not isinstance(value, dict):
                return False
            keys = value.keys()
            keybool = all(self._is_instance_of_type(k, args[0]) for k in keys)
            values = value.keys()
            valuebool = all(self._is_instance_of_type(v, args[1]) for v in values)
            return keybool and valuebool
        return False

    def set_number(self, num: int) -> int:
        return num

    def build(self) -> str:
        template = env.from_string(self.__class__.msg)
        input = asdict(self)
        return template.render(template=input).strip()


options_str = "[{% for opt in template.options.items() %}{{ opt[0] }} = {{ opt[1] }}{% if not loop.last %}, {% endif %}{% endfor %}]"

allowed_option_message_field = {"deprecated", "json_name", "packed"}


@dataclass
class MsgFieldLevelOptions(BaseTemplate):

    options: dict[str, str] = field(default_factory=dict)

    msg = options_str

    def add_option(self, key: str, value: Union[str, bool]):

        if not isinstance(key, str):
            raise TypeError("Field Level Option key should be a str")

        if key not in allowed_option_message_field:
            raise ValueError(
                f"Option {key} is not allowed for Field Level Options. Options key allowed is {allowed_option_message_field}"
            )

        if not isinstance(value, str) and not isinstance(value, bool):
            raise TypeError("Field Level Option value should be a bool or str")

        # FALTA COLCOAR PROTECAO PARA options que sao bool por natureza vs str
        # bool = packed e deprecated
        # str = json_name

        # falta colocar "" nos str

        if value is True:
            value = "true"
        elif value is False:
            value = "false"
        self.options[key] = value


stdfield_str = """
{% if template.comments -%}
// {{ template.comments }}
{% endif -%}
{{ template.type }} {{ template.name }} = {{ template.number }}{% if template.json_name %} [json_name = "{{ template.json_name }}"]{% endif %};
"""


@dataclass
class MsgFieldTemplate(BaseTemplate):
    type: str
    name: str
    number: int
    comments: Optional[str] = None
    json_name: Optional[str] = None

    def build(self) -> str:
        if self.comments is not None:
            self.comments = self.comments.lstrip("//")
        return super().build()

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
    listed: list[MsgFieldTemplate]

    msg = oneof_str

    def set_number(self, num: int):

        for stdtemp in self.listed:
            num = stdtemp.set_number(num)
        return num


block_str = """{{template.block}} {{ template.name }} {
{% for field in template.fields %}
  {{ field }}
{% endfor %}
}"""


@dataclass
class BlockTemplate(BaseTemplate):
    name: str
    fields: list[str]
    block: Optional[str] = None

    msg = block_str

    def __post_init__(self):
        return super().__post_init__()


@dataclass
class MessageTemplate(BlockTemplate):
    def __post_init__(self):
        self.block = "message"
        return super().__post_init__()


@dataclass
class MethodFieldLevelOptions(BaseTemplate): ...


mtd_field = """
{% if template.comments -%}
// {{ template.comments }}
{% endif -%}
rpc {{ template.method_name }}({% if template.client_streaming %}stream {% endif %}{{ template.request }}) returns ({% if template.server_streaming %}stream {% endif %}{{ template.response }}){
{% for option in template.options %}
  {{ option }}
{% endfor %}
};"""


@dataclass
class MethodFieldTemplate(BaseTemplate):
    method_name: str
    request_type: type
    response_type: type
    client_streaming: bool
    server_streaming: bool
    options: list[str] = field(default_factory=list)
    request: str = ""
    response: str = ""

    comments: str = ""
    msg = mtd_field

    def build(self) -> str:
        if self.comments is not None:
            self.comments = self.comments.lstrip("//")
        self.request = self.request_type.__name__
        self.response = self.response_type.__name__
        return super().build()


@dataclass
class ServiceTemplate(BlockTemplate):
    def __post_init__(self):
        self.block = "service"
        return super().__post_init__()


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
