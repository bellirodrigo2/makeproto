


from jinja2 import Environment

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

env = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
)

message_template = env.from_string(message_str)

protofile_template = env.from_string(protofile_str)