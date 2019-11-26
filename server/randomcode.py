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

func1(2, 3)
func1(2)
func2(2, [1, 2])
func2(2)

# what i leanred:
# when creating a decorator that returns a function that takes *args
# we must carefully consider the behavior of default parameters the original function had
# *args would only contain arguments that was explicitly passed