from makeproto.protobuilder import chain_dependants


def test_chain(requisition):
    cp = chain_dependants(requisition)
    # assert len(cp) == 7
