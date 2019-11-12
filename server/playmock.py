from unittest.mock import Mock, create_autospec
from database import Database

mock = Mock()
mock.searchPost.return_value = 9
mock.storePost.return_value = None

assert mock.searchPost() == 9
# assert mock.storePost() == None
print( mock.searchPost.call_count )
print( mock.storePost.call_count )

print( mock.searchPost.call_cnt ) # typo; still works
print( mock.searchItem.call_count ) # method that does not exist on database

# mock objects by default can spwan any method/attribute on the fly on its instance,
# making it difficult to track broken tests due to typos,
# or keeping up with changing api/interface specifications
# this problem can be tackled by auto-speccing an object
# auto-specced mock would force users of the mock to comply to the interface of the original object

mock = create_autospec(Database)
print( mock.searchPost('somecriteria') ) # existing method
# print( mock.searchPost() ) # existing method w/o required argument; throws exception
# print( mock.searchItem() ) # non-existing method; throws exception
print( mock.searchPost.call_count )
# print( mock.searchPost.call_cnt ) # typo; exception

# one caveat is that autospecc would not keep track of instance attributes:
class SomeClass:
    def __init__(self):
        self.foo = 'foo'

    def bar(self):
        print('bar')

mockSomeClass = create_autospec(SomeClass)
mockSomeClass.bar() # ok
# mockSomeClass.foo # error

# we can however set the attribute after mock is created
mockSomeClass.foo = 'foo'
print( mockSomeClass.foo ) # ok

# this behavior can be disabled by passing spec_set=True to constructor
mockSomeClass = create_autospec(SomeClass, spec_set=True)
# mockSomeClass.foo = 'foo' # error