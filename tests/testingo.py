class Base:
    clsarg:str = 'foobar'

class A(Base):...

class B(Base):...

A.clsarg = 'hello'
B.clsarg = 'world'

print(A.clsarg)

print(B.clsarg)

a = A()
print(a.clsarg)