from makeproto.builder.msgbuilder import make_message


def test_simple_user(msgs):
    
    user,_,_ = msgs
    
    res = make_message(user)
    
    assert 'message User {' in res
    assert 'int32 id = 0;' in res
    assert 'string name = 1;' in res
    assert 'string lastname = 2;'
    assert 'string email = 3;' in res
    assert 'int64 age = 4;' in res
    assert 'repeated string tags = 5;' in res
    

def test_simple_requisition(msgs):
    
    _,_,requisition = msgs
    
    res = make_message(requisition)
    
    assert 'message Requisition {' in res
    assert 'User user = 0;' in res
    assert 'Product product = 1;' in res
    assert 'int32 quantity = 2;' in res
    