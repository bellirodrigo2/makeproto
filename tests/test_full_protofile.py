import pytest
from makeproto.models import (
    Field, Method, Block, ProtoFile,
)
from makeproto.templates import render_protofile

# Campos básicos para reutilizar
field1 = Field.make("id", 1, "int32", comment="Unique ID", options={"deprecated": False})
field2 = Field.make("name", 2, "string", comment="Full name", options={"required": True})

# Enum simples
enum_block = Block.make(
    name="Status",
    block_type="enum",
    fields=[
        Field.make("UNKNOWN", 0),
        Field.make("ACTIVE", 1),
        Field.make("INACTIVE", 2),
    ],
    comment="/* Status of a record */",
    options={"allow_alias": True},
)

# OneOf dentro da message
oneof_block = Block.make(
    name="contact",
    block_type="oneof",
    fields=[
        Field.make("email", 3, "string", comment="User email", options={"required": True}),
        Field.make("phone", 4, "string", comment="User phone"),
    ],
    comment="/* Contact info, mutually exclusive */",
    options={"opt_oneof": "yes"},
)

# Message com fields e oneof
message_block = Block.make(
    name="User",
    block_type="message",
    fields=[
        field1,
        field2,
        oneof_block,
    ],
    comment="/* User entity */",
    options={"opt_msg": "enabled"},
)

# Serviço com métodos
method = Method.make(
    method_name="GetUser",
    request_type="UserRequest",
    response_type="User",
    request_stream=False,
    response_stream=False,
    comment="// Retrieves a user by ID",
    options={"idempotency_level": "IDEMPOTENT"},
)

service_block = Block.make(
    name="UserService",
    block_type="service",
    fields=[method],
    comment="/* Provides user operations */",
    options={"deprecated": False},
)

# ProtoFile
proto_file = ProtoFile.make(
    version=3,
    package_name="example.v1",
    blocks=[enum_block, message_block, service_block],
    comment="// Proto definitions for user management",
    options={"java_package": "com.example.user.v1"},
)


def test_protofile_rendering():
    result = render_protofile(proto_file)
    
    # Checks for syntax line
    assert "syntax = proto3;" in result

    # Package name
    assert "package example.v1;" in result

    # Global options
    assert 'option java_package = "com.example.user.v1";' in result

    # Enum
    assert "enum Status {" in result
    assert "UNKNOWN = 0;" in result
    assert "option allow_alias = true;" in result

    # Message
    assert "message User {" in result
    assert "int32 id = 1 [deprecated = false];" in result
    assert "string name = 2 [required = true];" in result
    assert "option opt_msg = \"enabled\";" in result

    # Oneof
    assert "oneof contact {" in result
    assert "option opt_oneof = \"yes\";" in result
    assert "string email = 3 [required = true];" in result
    assert "string phone = 4;" in result

    # Service
    assert "service UserService {" in result
    assert "rpc GetUser(UserRequest) returns (User) {" in result
    assert 'option idempotency_level = "IDEMPOTENT";' in result

    # Comments
    assert "/* User entity */" in result
    assert "/* Contact info, mutually exclusive */" in result
    assert "/* Provides user operations */" in result
    assert "// Retrieves a user by ID" in result


# Rodar com: pytest test_protofile_render.py -v
