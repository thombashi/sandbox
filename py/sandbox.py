# coding: utf-8

import timeit


print(timeit.repeat(stmt="""
type(1) == int
type(1) == str
"""))

print(timeit.repeat(stmt="""
isinstance(1, int)
isinstance(1, str)
"""))

print(timeit.repeat(stmt="""
isinstance(0.1, str) or isinstance(0.1, int)
"""))

print(timeit.repeat(stmt="""
isinstance(0.1, (int, str))
"""))

print(timeit.repeat(stmt="""
any([isinstance(0.1, str), isinstance(0.1, int)])
"""))

"""
def t():
    print("t")
    return True


def f():
    print("f")
    return False


print(any([t(), f(), t()]))

print("---")
print(t() or f() or t())
"""
