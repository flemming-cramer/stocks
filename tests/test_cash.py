import pytest
from unittest.mock import patch, PropertyMock
import streamlit as st

@pytest.fixture
def mock_streamlit():
    """Create a mock for streamlit with properly mocked session state."""
    with patch('ui.cash.st') as mock_st:
        # Use PropertyMock for cash value
        cash_value = PropertyMock(return_value=1000.0)
        type(mock_st.session_state).cash = cash_value
        type(mock_st.session_state).show_cash_form = PropertyMock(return_value=False)
        yield mock_st

def test_show_cash_section(mock_streamlit):
    """Test cash section display."""
    from ui.cash import show_cash_section
    show_cash_section()
    
    # Verify the calls
    mock_streamlit.subheader.assert_called_once_with("Cash Balance")
    mock_streamlit.metric.assert_called_once_with(
        label="Available Cash",
        value="$1,000.00"
    )