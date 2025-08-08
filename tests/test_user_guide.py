import pytest
from unittest.mock import patch, MagicMock
from ui.user_guide import show_user_guide

def test_show_user_guide():
    """Test user guide display."""
    mock_st = MagicMock()
    
    with patch('ui.user_guide.st', mock_st):
        show_user_guide()
        
        # Verify guide sections were displayed
        assert mock_st.markdown.called
        assert mock_st.subheader.called
        
        # Verify expander was created
        mock_st.expander.assert_called()