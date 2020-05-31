def test_me(a, b, c):
    d = 0
    if a > b + c:
        if b != c:
            d += 1
        else:
            d += 2
    else:
        d = d - 1
    
    if d > 0:
        if a > 0:
            return 1
        else:
            return 2
    else:
        return 3