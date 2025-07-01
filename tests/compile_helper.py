from pathlib import Path

import grpc_tools
from grpc_tools import protoc


def get_google_types_path() -> Path:
    return Path(grpc_tools.__file__).parent / "_proto"


def compile_protoc(
    proto_path: Path, protofile: str, output_dir: Path, add_google: bool = True
) -> bool:
    args = [
        "grpc_tools.protoc",
        f"--proto_path={str(proto_path)}",
        f"--python_out={str(output_dir)}",
        f"--grpc_python_out={str(output_dir)}",
        protofile,
    ]
    if add_google:
        google_path = get_google_types_path()
        args.insert(
            1,
            f"--proto_path={str(google_path)}",
        )
    result = protoc.main(args)
    if result == 0:
        return True
    else:
        raise Exception(f'Error compiling "{protofile}"')


if __name__ == "__main__":
    compile_protoc(
        Path("./tests/makeproto/proto"),
        "protofile.proto",
        Path("./tests//makeproto/proto"),
    )
