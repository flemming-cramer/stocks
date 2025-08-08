import pytest
import pandas as pd
import warnings
from unittest.mock import patch, PropertyMock, MagicMock
from ui.forms import (
    validate_buy_form,
    validate_sell_form,
    show_buy_form,
    show_sell_form
)

# Filter warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')
warnings.filterwarnings('ignore', category=FutureWarning, message='Calling float on a single element Series')

class MockSessionState(dict):
    """Mock class for Streamlit session state"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Portfolio and cash state with all required columns
        self.cash = 10000.0
        self.portfolio = pd.DataFrame({
            'ticker': ['AAPL'],
            'shares': [100],
            'price': [150.0],
            'buy_price': [150.0],
            'cost_basis': [15000.0],
            'stop_loss': [135.0]
        })
        
        # Buy form state
        self.b_price = 0.0
        self.b_shares = 0
        self.b_ticker = ''
        self.b_stop_pct = 0.0
        
        # Sell form state
        self.s_price = 0.0
        self.s_shares = 0
        self.s_ticker = 'AAPL'  # Set default value
        
        # Update with any provided values
        self.__dict__.update(kwargs)

@pytest.fixture
def mock_streamlit():
    """Create streamlit mock with proper session state."""
    mock_st = MagicMock()
    mock_st.session_state = MockSessionState()
    
    # Mock form context manager
    form_mock = MagicMock()
    form_mock.__enter__ = MagicMock(return_value=form_mock)
    form_mock.__exit__ = MagicMock(return_value=None)
    mock_st.form.return_value = form_mock
    
    # Mock number input with proper return value
    mock_st.number_input.return_value = 1.0
    
    # Mock selectbox with proper return value and tickers list
    mock_st.selectbox.return_value = 'AAPL'
    mock_st.session_state.portfolio['Ticker'] = ['AAPL']
    
    return mock_st

def test_validate_buy_form_valid():
    """Test buy form validation with valid data."""
    with patch('ui.forms.st.session_state.cash', 10000.0):
        data = {
            'ticker': 'AAPL',
            'shares': 10,
            'price': 150.0
        }
        assert validate_buy_form(data) is True

def test_validate_buy_form_invalid():
    """Test buy form validation with invalid data."""
    with patch('ui.forms.st.session_state.cash', 10000.0):
        invalid_cases = [
            ({}, False),  # Empty data
            ({'ticker': '', 'shares': 10, 'price': 150}, False),  # No ticker
            ({'ticker': 'AAPL', 'shares': -1, 'price': 150}, False),  # Negative shares
            ({'ticker': 'AAPL', 'shares': 1000, 'price': 150}, False),  # Insufficient funds
        ]
        
        for test_data, expected in invalid_cases:
            assert validate_buy_form(test_data) is expected

def test_show_buy_form(mock_streamlit):
    """Test buy form display."""
    with patch('ui.forms.st', mock_streamlit):
        show_buy_form('AAPL')
        
        # Verify form creation
        mock_streamlit.form.assert_called_once()
        
        # Verify input fields
        assert mock_streamlit.text_input.called
        assert mock_streamlit.number_input.call_count >= 2

def test_validate_sell_form_valid(mock_streamlit):
    """Test sell form validation with valid data."""
    with patch('ui.forms.st', mock_streamlit):
        # Set up mock portfolio with correct case
        mock_streamlit.session_state.portfolio = pd.DataFrame({
            'Ticker': ['AAPL'],
            'Shares': [100],  # Changed to uppercase
            'Price': [150.0]  # Changed to uppercase for consistency
        })
        mock_streamlit.session_state.s_ticker = 'AAPL'
        
        data = {
            'ticker': 'AAPL',
            'shares': 50,
            'price': 160.0
        }
        assert validate_sell_form(data) is True

def test_validate_sell_form_invalid(mock_streamlit):
    """Test sell form validation with invalid data."""
    with patch('ui.forms.st', mock_streamlit):
        # Set up mock portfolio with correct case
        mock_streamlit.session_state.portfolio = pd.DataFrame({
            'Ticker': ['AAPL'],
            'Shares': [100],  # Changed to uppercase
            'Price': [150.0]  # Changed to uppercase for consistency
        })
        mock_streamlit.session_state.s_ticker = 'AAPL'
        
        invalid_cases = [
            ({}, False),
            ({'ticker': '', 'shares': 10, 'price': 150}, False),
            ({'ticker': 'AAPL', 'shares': -1, 'price': 150}, False),
            ({'ticker': 'AAPL', 'shares': 200, 'price': 150}, False),
        ]
        
        for test_data, expected in invalid_cases:
            assert validate_sell_form(test_data) is expected

def test_show_sell_form(mock_streamlit):
    """Test sell form display."""
    with patch('ui.forms.st', mock_streamlit):
        # Create portfolio data with correct column names
        portfolio_data = pd.DataFrame({
            'ticker': ['AAPL'],
            'shares': [100],
            'price': [150.0],
            'buy_price': [150.0],
            'cost_basis': [15000.0],
            'stop_loss': [135.0]
        })
        
        # Update mock_streamlit to match actual implementation
        mock_streamlit.session_state.portfolio = portfolio_data
        mock_streamlit.selectbox.return_value = 'AAPL'
        
        show_sell_form()
        
        # Verify form creation
        mock_streamlit.form.assert_called_once()
        
        # Update assertion to match actual implementation
        mock_streamlit.selectbox.assert_called_with(
            'Ticker',
            options=['Select a Ticker', 'AAPL'],
            index=0
        )
        assert mock_streamlit.number_input.call_count >= 1