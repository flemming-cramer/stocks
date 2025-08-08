import pytest
from ui.dashboard import fmt_currency, fmt_percent, fmt_shares

def test_fmt_currency():
    """Test currency formatting."""
    assert fmt_currency(1234.5678) == '$1,234.57'
    assert fmt_currency(-1234.56) == '-$1,234.56'
    assert fmt_currency(0) == '$0.00'
    assert fmt_currency('invalid') == ''

def test_fmt_percent():
    """Test percentage formatting."""
    assert fmt_percent(12.345) == '+12.3% ↑'
    assert fmt_percent(-12.345) == '-12.3% ↓'
    assert fmt_percent(0) == '0.0%'
    assert fmt_percent('invalid') == ''

def test_fmt_shares():
    """Test share count formatting."""
    assert fmt_shares(1234) == '1,234'
    assert fmt_shares(1234.56) == '1,234'
    assert fmt_shares(0) == '0'
    assert fmt_shares('invalid') == ''