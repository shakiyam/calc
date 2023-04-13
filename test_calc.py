from calc import calculate


def test_calculate():
    assert calculate('1 + 1', 0) == '2'
    assert calculate('1 + ? x 3,000', 2) == '6,001'
    assert calculate('00:01:00 + 123sec', '6,001') == '00:03:03'
