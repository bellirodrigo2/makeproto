from makeproto.build_service import compile_service
from tests.conftest import Service, write_template


def test_protofile_basic(
    simple_service: Service,
) -> None:
    proto_stream = compile_service({"": [simple_service]})
    proto_package = list(proto_stream)[0]
    rendered = proto_package.content
    write_template(rendered, proto_package.filename, 4)


def test_empty() -> None:
    compile_service({"empty": []})


def test_invalid_package_name(
    simple_service: Service,
) -> None:
    pack1 = "pack1"
    service = Service(name="invalid name", package=pack1)
    pack2 = "pack2"
    service2 = Service(name="serv", package=pack2)
    service3 = Service(name="serv", package=pack2)
    compile_service(
        {"": [simple_service], pack1: [service], pack2: [service2, service3]}
    )
