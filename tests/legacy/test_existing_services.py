import pytest
from unittest.mock import patch
from services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist
)

def test_existing_watchlist_service():
    """Test existing watchlist service functions."""
    # These should work with the existing implementation
    with patch('services.watchlist_service.st') as mock_st:
        # Mock session state
        mock_st.session_state.watchlist_state.tickers = set()
        
        # Test basic operations
        add_to_watchlist('AAPL')
        assert 'AAPL' in mock_st.session_state.watchlist_state.tickers
        
        remove_from_watchlist('AAPL')
        assert 'AAPL' not in mock_st.session_state.watchlist_state.tickers