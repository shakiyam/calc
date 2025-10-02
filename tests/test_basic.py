from calc.__main__ import evaluate_expression


def test_basic_operators():
    """Test basic mathematical operators"""
    last_result_val = '0'
    success, value, error = evaluate_expression('10 - 3', last_result_val)
    assert success and value == '7'
    success, value, error = evaluate_expression('12 / 4', last_result_val)
    assert success and value == '3'
    success, value, error = evaluate_expression('7 % 3', last_result_val)
    assert success and value == '1'
    success, value, error = evaluate_expression('2 ** 3', last_result_val)
    assert success and value == '8'
    success, value, error = evaluate_expression('(2 + 3) * 4', last_result_val)
    assert success and value == '20'
    success, value, error = evaluate_expression('-5 * -3', last_result_val)
    assert success and value == '15'


def test_operator_aliases():
    """Test operator aliases"""
    last_result_val = '0'
    success, value, error = evaluate_expression('10 ＋ 5', last_result_val)
    assert success and value == '15'
    success, value, error = evaluate_expression('20 － 8', last_result_val)
    assert success and value == '12'
    success, value, error = evaluate_expression('3 x 4', last_result_val)
    assert success and value == '12'
    success, value, error = evaluate_expression('5 X 2', last_result_val)
    assert success and value == '10'
    success, value, error = evaluate_expression('2x3', last_result_val)
    assert success and value == '6'
    success, value, error = evaluate_expression('(2+3)x4', last_result_val)
    assert success and value == '20'
    success, value, error = evaluate_expression('6 × 7', last_result_val)
    assert success and value == '42'
    success, value, error = evaluate_expression('18 ÷ 3', last_result_val)
    assert success and value == '6'
    success, value, error = evaluate_expression('2 ^ 3', last_result_val)
    assert success and value == '8'


def test_decimal_precision():
    """Test that decimal calculations are precise"""
    last_result_val = '0'
    success, value, error = evaluate_expression('0.1 + 0.2', last_result_val)
    assert success and value == '0.3'
    success, value, error = evaluate_expression('1 / 3 * 3', last_result_val)
    assert success and value == '1'


def test_comments():
    """Test that comments are ignored"""
    last_result_val = '0'
    success, value, error = evaluate_expression('1 + 1 # This is a comment', last_result_val)
    assert success and value == '2'
    success, value, error = evaluate_expression('# Just a comment', last_result_val)
    assert success and value == last_result_val


def test_input_formatting():
    """Test comma handling and number formatting"""
    last_result_val = '0'
    success, value, error = evaluate_expression('1,000 + 2,000', last_result_val)
    assert success and value == '3,000'
    success, value, error = evaluate_expression('1000000', last_result_val)
    assert success and value == '1,000,000'


def test_history_functionality():
    """Test history reference with ?"""
    last_result_val = '0'
    success, value, error = evaluate_expression('5 + 3', last_result_val)
    assert success and value == '8'
    success, value, error = evaluate_expression('? * 2', '8')
    assert success and value == '16'
    success, value, error = evaluate_expression('? + ?', '16')
    assert success and value == '32'


def test_unit_removal():
    """Test removal of non-time units from expressions"""
    last_result_val = '0'
    success, value, error = evaluate_expression('10個 + 20個', last_result_val)
    assert success and value == '30'
    success, value, error = evaluate_expression('100 円 - 50 円', last_result_val)
    assert success and value == '50'
    success, value, error = evaluate_expression('10.5kg * 2', last_result_val)
    assert success and value == '21.0'
    success, value, error = evaluate_expression('1,024 GB / 4', last_result_val)
    assert success and value == '256'
