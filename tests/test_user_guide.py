import pytest
from unittest.mock import patch
from tests.mock_streamlit import StreamlitMock
from ui.user_guide import show_user_guide

def test_show_user_guide():
    """Test user guide display."""
    mock_st = StreamlitMock()
    with patch('ui.user_guide.st', mock_st):
        show_user_guide()
        assert mock_st.assert_called('expander')
        assert mock_st.assert_called('subheader')
        assert mock_st.assert_called('markdown')