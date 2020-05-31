import TestGen2


def test_me(x):
    z = 0
    if x == 2:
        TestGen2.check_branch(1, 0, ['x', 'z'], x, z)
        return z
    else:
        TestGen2.check_branch(1, 1, ['x', 'z'], x, z)
    for i in range(x):
        TestGen2.check_branch(2, 0, ['x', 'z'], x, z)
        z += 1
    else:
        TestGen2.check_branch(2, 1, ['x', 'z'], x, z)
        if z == 0:
            TestGen2.check_branch(3, 0, ['x', 'z'], x, z)
            return x
        else:
            TestGen2.check_branch(3, 1, ['x', 'z'], x, z)
        while z > 0:
            TestGen2.check_branch(4, 0, ['x', 'z'], x, z)
            z -= 1
        else:
            TestGen2.check_branch(4, 1, ['x', 'z'], x, z)
    return z
