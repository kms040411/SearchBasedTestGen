import TestGen


def test_me(x, y, z):
    a = 0
    b = 0
    c = 0
    if x == 4:
        TestGen.check_branch(1, 1)
        print('1')
        a += 1
        if x + y == 100:
            TestGen.check_branch(2, 1)
            print('2')
            a += 1
            if z > 112831829389:
                TestGen.check_branch(3, 1)
                print('3')
                a += 1
            else:
                TestGen.check_branch(3, 0)
                print('4')
        else:
            TestGen.check_branch(2, 0)
            if x + y == 40:
                TestGen.check_branch(4, 1)
                print('5')
            else:
                TestGen.check_branch(4, 0)
    else:
        TestGen.check_branch(1, 0)
