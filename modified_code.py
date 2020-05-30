import TestGen2


def test_me(a, b, c):
    d = 0
    if a > b + c:
        TestGen2.check_branch(1, 0, ['a', 'b', 'c', 'd'], a, b, c, d)
        print('1')
        if b != c:
            TestGen2.check_branch(2, 0, ['a', 'b', 'c', 'd'], a, b, c, d)
            print('2')
            d += 1
        else:
            TestGen2.check_branch(2, 1, ['a', 'b', 'c', 'd'], a, b, c, d)
            print('3')
            d += 2
    else:
        TestGen2.check_branch(1, 1, ['a', 'b', 'c', 'd'], a, b, c, d)
        print('4')
        d = d - 1
    if d > 0:
        TestGen2.check_branch(3, 0, ['a', 'b', 'c', 'd'], a, b, c, d)
        print('5')
        if a > 0:
            TestGen2.check_branch(4, 0, ['a', 'b', 'c', 'd'], a, b, c, d)
            print('6')
            return 1
        else:
            TestGen2.check_branch(4, 1, ['a', 'b', 'c', 'd'], a, b, c, d)
            print('7')
            return 2
    else:
        TestGen2.check_branch(3, 1, ['a', 'b', 'c', 'd'], a, b, c, d)
        print('8')
        return 3
