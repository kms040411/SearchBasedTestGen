def test_me(x):
    z = 0
    if x == 2:
        return z
    for i in range(x):
        z += 1
    else:
        if z == 0:
            return x
        while z > 0:
            z -= 1
    return z
