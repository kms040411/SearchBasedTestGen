import TestGen


def test_me(x, y, z):
    if y == 100003:
        TestGen.check_branch(1, 1)
        print('1')
        z = 1
    else:
        TestGen.check_branch(1, 0)
        print('2')
        x = 2
