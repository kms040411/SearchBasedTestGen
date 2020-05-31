import TestGen2


def test_me(a, b, c):
    d = 0
    if a > b + c:
        TestGen2.check_branch(1, 0, ['a', 'b', 'c', 'd'], a, b, c, d)
        if b != c:
            TestGen2.check_branch(2, 0, ['a', 'b', 'c', 'd'], a, b, c, d)
            d += 1
        else:
            TestGen2.check_branch(2, 1, ['a', 'b', 'c', 'd'], a, b, c, d)
            d += 2
    else:
        TestGen2.check_branch(1, 1, ['a', 'b', 'c', 'd'], a, b, c, d)
        d = d - 1
    if d > 0:
        TestGen2.check_branch(3, 0, ['a', 'b', 'c', 'd'], a, b, c, d)
        if a > 0:
            TestGen2.check_branch(4, 0, ['a', 'b', 'c', 'd'], a, b, c, d)
            return 1
        else:
            TestGen2.check_branch(4, 1, ['a', 'b', 'c', 'd'], a, b, c, d)
            return 2
    else:
        TestGen2.check_branch(3, 1, ['a', 'b', 'c', 'd'], a, b, c, d)
        return 3
