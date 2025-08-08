import pytest
import pandas as pd
from ui.dashboard import format_currency, format_percentage

def test_format_currency():
    """Test currency formatting."""
    assert format_currency(1234.5678) == "$1,234.57"
    assert format_currency(0) == "$0.00"
    assert format_currency(-1234.56) == "-$1,234.56"

def test_format_percentage():
    """Test percentage formatting."""
    assert format_percentage(0.1234) == "12.34%"
    assert format_percentage(-0.1234) == "-12.34%"
    assert format_percentage(0) == "0.00%"