import pytest
from unittest.mock import patch
import streamlit as st
from ui.cash import show_cash_section

@pytest.fixture
def mock_session_state():
    if 'cash' not in st.session_state:
        st.session_state.cash = 1000.0
    return st.session_state

def test_show_cash_section(mock_session_state):
    """Test cash section display."""
    with patch('streamlit.metric') as mock_metric:
        show_cash_section()
        mock_metric.assert_called_once()
        args, kwargs = mock_metric.call_args
        assert kwargs['value'].startswith('$')