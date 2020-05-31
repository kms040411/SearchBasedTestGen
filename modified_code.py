import TestGen2


def test1(x):
    if x > 3:
        TestGen2.check_branch(1, 0, ['x'], x)
        a = 5
    else:
        TestGen2.check_branch(1, 1, ['x'], x)
    if x < -3:
        TestGen2.check_branch(2, 0, ['x'], x)
        a = -5
    else:
        TestGen2.check_branch(2, 1, ['x'], x)


def test2(x):
    if x > 5:
        TestGen2.check_branch(1, 0, ['x'], x)
        a = 5
    else:
        TestGen2.check_branch(1, 1, ['x'], x)
        a = -5
