from makeproto.protobuilder import chain_dependants


def test_chain(requisition):
    chain_dependants(requisition)
    # assert len(cp) == 7
