import TestGen2


def test_me(x, y):
    if y != 0:
        TestGen2.check_branch(1, 0, ['x', 'y'], x, y)
        a = 0
    else:
        TestGen2.check_branch(1, 1, ['x', 'y'], x, y)
    if x != 5:
        TestGen2.check_branch(2, 0, ['x', 'y'], x, y)
        a = 5
    else:
        TestGen2.check_branch(2, 1, ['x', 'y'], x, y)
    if x != 6:
        TestGen2.check_branch(3, 0, ['x', 'y'], x, y)
        a = 6
    else:
        TestGen2.check_branch(3, 1, ['x', 'y'], x, y)
    if x != 7:
        TestGen2.check_branch(4, 0, ['x', 'y'], x, y)
        a = 6
    else:
        TestGen2.check_branch(4, 1, ['x', 'y'], x, y)
    if y == 0:
        TestGen2.check_branch(5, 0, ['x', 'y'], x, y)
        a = 0
    else:
        TestGen2.check_branch(5, 1, ['x', 'y'], x, y)
    if x == 5:
        TestGen2.check_branch(6, 0, ['x', 'y'], x, y)
        a == 5
    else:
        TestGen2.check_branch(6, 1, ['x', 'y'], x, y)
    if x == 6:
        TestGen2.check_branch(7, 0, ['x', 'y'], x, y)
        a == 6
    else:
        TestGen2.check_branch(7, 1, ['x', 'y'], x, y)
