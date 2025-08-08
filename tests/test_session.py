import pytest
import streamlit as st
from services.session import init_session_state

def test_init_session_state():
    """Test session state initialization."""
    init_session_state()
    
    # Verify all required keys are initialized
    assert 'portfolio' in st.session_state
    assert 'watchlist' in st.session_state
    assert 'watchlist_prices' in st.session_state
    assert 'cash' in st.session_state