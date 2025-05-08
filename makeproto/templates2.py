from dataclasses import asdict, dataclass
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Union

# Configurar o ambiente Jinja2
env = Environment(loader=FileSystemLoader("templates"))

# Carregar os templates
field_template = env.get_template("field.j2")
block_template = env.get_template("block.j2")
method_template = env.get_template("method.j2")

def format_option(item: tuple[str, Union[str, bool]]):
    key, value = item
    if isinstance(value, bool):  # Verifica se o valor é um booleano
        value = 'true' if value else 'false'  # Converte True para 'true' e False para 'false'
    elif isinstance(value, str):  # Se for uma string, mantemos o valor entre aspas
        value = f'"{value}"'
    return f'{key} = {value}'


@dataclass
class Field:
    type: str
    name: str
    number: int
    options: dict[str, Union[str, bool]]

def make_message(name: str, fields: List[Field], comment: str = "") -> str:
    """
    Gera a definição de uma mensagem com seus campos, usando os templates Jinja2.

    :param name: Nome da mensagem.
    :param fields: Lista de campos, onde cada campo é um dicionário com chaves `type`, `name`, `number` e opcionalmente `options`.
    :param comment: Comentário a ser adicionado antes da definição (opcional).
    :return: String com a definição completa da mensagem.
    """
    
    # Renderizar os campos usando o template field.j2
    fields_rendered = [
        field_template.render(**asdict(field))  # Correção aqui: deve ser asdict(field) para cada field
        for field in fields
    ]
    
    # Renderizar o bloco completo com a definição da mensagem
    message_definition = block_template.render(
        comment=comment,
        template={"block": "message", "name": name},
        fields=fields_rendered
    )
    
    return message_definition  # Faltava o retorno aqui


@dataclass
class Method:
    method_name: str
    request_type: str
    response_type: str
    request_stream: bool
    response_stream: bool
    options: Dict[str, Union[str, bool]]


def make_service(name: str, methods: List[Method], comment: str = "") -> str:
    """
    Gera a definição de um serviço com seus métodos, usando os templates Jinja2.

    :param name: Nome do serviço.
    :param methods: Lista de métodos, onde cada método é uma instância de `Method`.
    :param comment: Comentário a ser adicionado antes da definição (opcional).
    :return: String com a definição completa do serviço.
    """
    
    # Renderizar os métodos usando o template method.j2
    methods_rendered = [
        method_template.render(
            method_name=method.method_name,
            request_type=method.request_type,
            response_type=method.response_type,
            request_stream=method.request_stream,
            response_stream=method.response_stream,
            options=method.options
        )
        for method in methods
    ]
    
    # Renderizar o bloco completo com a definição do serviço
    service_definition = block_template.render(
        comment=comment,
        template={"block": "service", "name": name},
        fields=methods_rendered  # Usando "fields" para o mesmo conceito de "methods"
    )
    
    return service_definition  # Retorna a definição do serviço gerado
