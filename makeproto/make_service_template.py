from typing import Any, Callable, List, Type

from makeproto.interface import IService
from makeproto.template import MethodTemplate, ServiceTemplate

# def is_message(bt: Any, msg_type: Type[Any]) -> bool:
#     return isinstance(bt, type) and issubclass(bt, msg_type)


# def get_message(tgt: Optional[Type[Any]], msg_type: Type[Any]) -> Optional[type[Any]]:

#     if tgt is None:
#         return None

#     basetype = if_stream_get_type(tgt)
#     bt = basetype or tgt
#     if is_message(bt, msg_type):
#         return bt
#     return None


# def extract_request(
#     func: Callable[..., Any], tgt_instance: Type[Any], msg_type: Type[Any]
# ) -> List[Type[Any]]:
#     funcargs = get_func_args(func)
#     requests: Set[Type[Any]] = set()

#     for arg in funcargs:
#         instance = arg.getinstance(tgt_instance)
#         if get_message(arg.basetype, msg_type):
#             requests.add(arg.basetype)
#         elif instance is not None:
#             model = instance.model
#             if not is_message(model, msg_type):
#                 raise TypeError(
#                     f'On function "{func.__name__}", argument "{arg.name}", FromRequest uses an invalid model: "{model}"'
#                 )
#             requests.add(model)

#     return list(requests)


def make_service_template(
    service: IService,
    extract_requests: Callable[..., List[Type[Any]]],
    extract_response: Callable[..., Type[Any]],
) -> ServiceTemplate:

    service_template = ServiceTemplate(
        name=service.name,
        package=service.package,
        module=service.module,
        comments=service.comments,
        options=service.options,
        methods=[],
    )
    methods: List[MethodTemplate] = []

    for labeledmethod in service.methods:
        method = labeledmethod.method

        requests = extract_requests(method)
        response_type = extract_response(method)

        method_template = MethodTemplate(
            method_func=method,
            name=method.__name__,
            options=labeledmethod.options,
            comments=labeledmethod.comments,
            request_types=requests,
            response_type=response_type,
            service=service_template,
            request_stream=False,
            response_stream=False,
        )
        methods.append(method_template)
    service_template.methods = methods
    return service_template
