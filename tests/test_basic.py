from calc.__main__ import calculate


def test_basic_operators():
    """Test all supported operators and aliases"""
    last_result_val = '0'
    assert calculate('10 - 3', last_result_val) == '7'
    assert calculate('12 / 4', last_result_val) == '3'
    assert calculate('7 % 3', last_result_val) == '1'
    assert calculate('2 ** 3', last_result_val) == '8'
    assert calculate('3 x 4', last_result_val) == '12'
    assert calculate('(2 + 3) * 4', last_result_val) == '20'
    assert calculate('-5 * -3', last_result_val) == '15'


def test_decimal_precision():
    """Test that decimal calculations are precise"""
    last_result_val = '0'
    assert calculate('0.1 + 0.2', last_result_val) == '0.3'
    assert calculate('1 / 3 * 3', last_result_val) == '1'


def test_comments():
    """Test that comments are ignored"""
    last_result_val = '0'
    assert calculate('1 + 1 # This is a comment', last_result_val) == '2'
    assert calculate('# Just a comment', last_result_val) == last_result_val


def test_input_formatting():
    """Test comma handling and number formatting"""
    last_result_val = '0'
    assert calculate('1,000 + 2,000', last_result_val) == '3,000'
    assert calculate('1000000', last_result_val) == '1,000,000'


def test_history_functionality():
    """Test history reference with ?"""
    last_result_val = '0'
    assert calculate('5 + 3', last_result_val) == '8'
    assert calculate('? * 2', '8') == '16'
    assert calculate('? + ?', '16') == '32'


def test_unit_removal():
    """Test removal of non-time units from expressions"""
    last_result_val = '0'
    assert calculate('10個 + 20個', last_result_val) == '30'
    assert calculate('100 円 - 50 円', last_result_val) == '50'
    assert calculate('10.5kg * 2', last_result_val) == '21.0'
    assert calculate('1,024 GB / 4', last_result_val) == '256'
