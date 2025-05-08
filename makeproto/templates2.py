from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Union

from jinja2 import Environment, FileSystemLoader
from makeproto.models import Block, Field, Method, OneOfBlock, ProtoFile

def render_obj(temp:Union[Field, Method]):

    template = None
    if isinstance(temp, Field):
        template = field_template
    if isinstance(temp, Method):
        template = method_template    
    if isinstance(temp, Block):
        template = block_template
    
    if template is None:
        raise TypeError(f'Cant Resolve template for obj of class "{type(temp)}"')
    return template.render(**asdict(temp))

def render_block(block: Block[Union[Field, Method, OneOfBlock]], comment: str = "") -> str:

    if not block.fields:
        raise ValueError(f"Rendering Block '{block.name}' is empty.")

    rendered_items = [render_obj(item) for item in block.fields]

    return block_template.render(
        comment=comment,
        template={"block": block.block_type, "name": block.name},
        fields=rendered_items,
        options=block.options or {},  # Passar as opções para o template
    )


def render_protofile(proto_file: ProtoFile) -> str:
    rendered_blocks = [render_block(block) for block in proto_file.blocks]

    return proto_template.render(
        version=proto_file.version or 3,  # Define a versão 'proto3' como padrão
        package_name=proto_file.package_name,
        options=proto_file.options or {},  # Passa as opções globais, se houver
        blocks=rendered_blocks,  # Passa os blocos renderizados
    )


def make_env(path: Path, filters: dict[str, Callable[...,Any]]):

    env = Environment(loader=FileSystemLoader(str(path)))
    for k,v in filters.items():
        env.filters[k] = v
    return env


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def format_option(item: tuple[str, Union[str, bool]]):
    key, value = item
    if isinstance(value, bool):
        value = "true" if value else "false"
    elif isinstance(value, str):
        value = f'"{value}"'
    return f"{key} = {value}"


def format_comment(raw_comment: str, line_limit: int = 80) -> str:
    stripped = raw_comment.strip()
    if stripped.startswith("//"):
        return stripped
    if stripped.startswith("/*") and stripped.endswith("*/"):
        return stripped
    if stripped.startswith("/*") and not stripped.endswith("*/"):
        return stripped + " */"
    if "\n" not in stripped and len(stripped) <= line_limit:
        return f"// {stripped}"
    lines = stripped.splitlines()
    cleaned_lines = [line.strip() for line in lines]
    block = "\n".join(f" * {line}" for line in cleaned_lines)
    return f"/*\n{block}\n */"

filters:dict[str,Callable[...,Any]] = {
    "format_option": format_option,
    "format_comment": format_comment
}
env = make_env(TEMPLATES_DIR, filters)

field_template = env.get_template("field.j2")
block_template = env.get_template("block.j2")
method_template = env.get_template("method.j2")
proto_template = env.get_template("protofile.j2")
