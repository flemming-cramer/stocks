import pytest
import pandas as pd
import streamlit as st
from ui.forms import validate_buy_form, validate_sell_form

@pytest.fixture(autouse=True)
def mock_session_state():
    """Setup session state before each test."""
    if 'cash' not in st.session_state:
        st.session_state.cash = 2000.0  # Enough cash for test transactions
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=['Ticker', 'Shares', 'Price'])
    return st.session_state

def test_validate_buy_form(mock_session_state):
    """Test buy form validation."""
    valid_data = {
        'ticker': 'AAPL',
        'shares': 10,
        'price': 150.0
    }
    assert validate_buy_form(valid_data) is True
    
    # Test invalid cases
    invalid_data = [
        {'ticker': '', 'shares': 10, 'price': 150.0},  # Empty ticker
        {'ticker': 'AAPL', 'shares': -1, 'price': 150.0},  # Negative shares
        {'ticker': 'AAPL', 'shares': 10, 'price': 0},  # Zero price
        {'ticker': 'AAPL', 'shares': 1000, 'price': 150.0},  # Insufficient funds
    ]
    
    for data in invalid_data:
        assert validate_buy_form(data) is False

def test_validate_sell_form():
    """Test sell form validation."""
    st.session_state.portfolio = pd.DataFrame({
        'Ticker': ['AAPL'],
        'Shares': [10],
        'Price': [150.0]
    })
    
    valid_data = {
        'ticker': 'AAPL',
        'shares': 5,
        'price': 160.0
    }
    assert validate_sell_form(valid_data) is True
    
    invalid_data = {
        'ticker': 'AAPL',
        'shares': 20,  # More than owned
        'price': 160.0
    }
    assert validate_sell_form(invalid_data) is False