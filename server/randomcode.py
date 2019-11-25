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