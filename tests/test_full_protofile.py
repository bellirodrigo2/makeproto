from pathlib import Path


from makeproto.models import Block, Field, Method, ProtoFile
from makeproto.prototypes import EnumOption
from makeproto.templates import render_protofile
from makeproto.compile_proto import compile

# Campos reutilizáveis
field1 = Field.make(
    "id", 1, "int32", comment="Unique ID", options={"deprecated": False}
)
field2 = Field.make("name", 2, "string", comment="Full name")  # REMOVIDO 'required'

# Enum
enum_block = Block.make(
    protofile='proto1',
    package='package1',
    name="Status",
    block_type="enum",
    fields=[
        Field.make("UNKNOWN", 0),
        Field.make("ACTIVE", 1),
        Field.make("INACTIVE", 2),
    ],
    comment="/* Status of a record */",
)

# OneOf block
oneof_block = Block.make(
    protofile='proto1',
    package='package1',
    name="contact",
    block_type="oneof",
    fields=[
        Field.make("email", 3, "string", comment="User email"),  # REMOVIDO 'required'
        Field.make("phone", 4, "string", comment="User phone"),
    ],
    comment="/* Contact info, mutually exclusive */",
)

# Mensagem User
message_block = Block.make(
    protofile='proto1',
    package='package1',
    name="User",
    block_type="message",
    fields=[
        field1,
        field2,
        oneof_block,
    ],
    comment="/* User entity */",
)

# Mensagem UserRequest — AGORA DEFINIDA
user_request_block = Block.make(
    protofile='proto1',
    package='package1',
    name="UserRequest",
    block_type="message",
    fields=[
        Field.make("user_id", 1, "int32", comment="ID of the user"),
    ],
    comment="/* Request message to get a user by ID */",
)


class UserRequest: ...


class User: ...


# Método com idempotency_level — SEM aspas
method = Method.make(
    method_name="GetUser",
    request_type=UserRequest,
    response_type=User,
    request_stream=False,
    response_stream=False,
    comment="// Retrieves a user by ID",
    options={
        "idempotency_level": EnumOption("IDEMPOTENT")
    },  # Atenção: isso só compila se importar descriptor.proto corretamente
)

service_block = Block.make(
    protofile='proto1',
    package='package1',
    name="UserService",
    block_type="service",
    fields=[method],
    comment="/* Provides user operations */",
    options={"deprecated": False},
)

# Arquivo Proto
fname = "teste_full.proto"

proto_file = ProtoFile.make(
    version=3,
    protofile_name=fname,
    package_name="example.v1",
    imports=["google/api/client.proto"],
    blocks=[enum_block, user_request_block, message_block, service_block],
    comment="// Proto definitions for user management",
    options={"java_package": "com.example.user.v1"},
)


def test_protofile_rendering():
    result = render_protofile(proto_file)

    assert 'syntax = "proto3";' in result
    assert "package example.v1;" in result
    assert 'option java_package = "com.example.user.v1";' in result

    assert "enum Status {" in result
    assert "UNKNOWN = 0;" in result

    assert "message UserRequest {" in result
    assert "int32 user_id = 1;" in result

    assert "message User {" in result
    assert "int32 id = 1 [deprecated = false];" in result
    assert "string name = 2;" in result

    assert "oneof contact {" in result
    assert "string email = 3;" in result
    assert "string phone = 4;" in result

    assert "service UserService {" in result
    assert "rpc GetUser(UserRequest) returns (User) {" in result
    assert "option idempotency_level = IDEMPOTENT;" in result

    assert "/* User entity */" in result
    assert "/* Contact info, mutually exclusive */" in result
    assert "/* Provides user operations */" in result
    assert "// Retrieves a user by ID" in result

    folder = Path(__file__).parent / "proto"
    file = folder / fname
    with open(file, "w", encoding="utf-8") as f:
        f.write(result)
    compile(folder, fname, folder / "compiled")
