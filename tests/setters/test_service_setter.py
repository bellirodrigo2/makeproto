from makeproto.compiler import CompilerContext
from makeproto.setters.service import ServiceSetter
from makeproto.template import ProtoTemplate
from tests.test_helpers import make_service


def test_duplicated_service() -> None:
    validator = ServiceSetter()
    mod = "mod"
    block = make_service("ValidBlock", module=mod)
    context = CompilerContext(state={mod: ProtoTemplate("", 3, "", mod, set(), [], [])})

    validator.execute([block, block], context)
    assert len(context) == 1
