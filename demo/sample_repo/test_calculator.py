from calculator import calculate_discount


def test_twenty_percent_discount():
    result = calculate_discount(100, 20)
    assert result == 80