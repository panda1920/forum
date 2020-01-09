import urllib.parse
from pathlib import Path

class SomeClass:
    def __init__(self):
        print('parent init')

class DerivedClass1(SomeClass):
    pass

class DerivedClass2(SomeClass):
    def __init__(self):
        print('child init')

def discoverConstructorBehavior():
    SomeClass()
    print('================')
    DerivedClass1()
    print('================')
    DerivedClass2()
    print('================')

# what I learned:
# When creating a constructor for derived classes,
# Parent constructor would not be called unless it is explicitly invoked through super().__init__()

def countArgs(f):
    def wrapper(*args):
        f(*args)
        print(args)
        print( len(args) )
    return wrapper

@countArgs
def func1(a, b = None):
    pass

@countArgs
def func2(a, b = []):
    pass

def seeArgsPassedToDecoratedFunc():
    func1(2, 3)
    func1(2)
    func2(2, [1, 2])
    func2(2)

# what i leanred:
# when creating a decorator that returns a function that takes *args
# we must carefully consider the behavior of default parameters the original function had
# *args would only contain arguments that was explicitly passed

def cerberusChecker():
    from cerberus import Validator

    schema1 = {
        'name': {
            'type': 'string',
            'maxlength': 10,
            'required': True,
        }
    }
    documents = [
        {'name': 'Mark'},
        {'name': 'Markiplier200'},
        {'name': 'John', 'id': '2211'},
        {'name': 22},
    ]

    for document in documents:
        v = Validator(allow_unknown=True)
        validated = v.validate(document, schema1)
        if not validated:
            print(v.errors)

    schema2 = {
        'id': {
            'type': 'integer',
            'coerce': int,
            'default': 100,
            'required': True,
        }
    }
    documents = [
        {'id': 2233},
        {'id': '2233'},
        {},
        {'id': 'some_string'},

    ]
    v = Validator(schema=schema2)
    for document in documents:
        print(v.validate(document))
        print(v.errors)
        print(v.document)
        print(v.normalized(document))

cerberusChecker()