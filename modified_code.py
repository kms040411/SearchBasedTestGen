import TestGen


def test_me(x, y, z):
    if y > 13:
        TestGen.check_branch(1, 1)
        print('1')
        if x < 2:
            TestGen.check_branch(2, 1)
            print('2')
            z = 3
            if x < -1:
                TestGen.check_branch(3, 1)
                print('3')
                z = 1
            else:
                TestGen.check_branch(3, 0)
        else:
            TestGen.check_branch(2, 0)
    else:
        TestGen.check_branch(1, 0)
        print('4')
        x = 2
    y = 50
    if z == 4:
        TestGen.check_branch(4, 1)
        print('5')
        z = 1
    else:
        TestGen.check_branch(4, 0)
        print('6')
        while x < 5:
            TestGen.check_branch(5, 1)
            print('7')
            x += 1
            z = z + 1
        else:
            TestGen.check_branch(5, 0)
    y = 0
