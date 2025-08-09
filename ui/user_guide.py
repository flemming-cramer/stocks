import streamlit as st


def show_user_guide() -> None:
    """Display the user guide with helpful information."""
    with st.expander("📚 User Guide", expanded=False):
        st.subheader("Getting Started")
        st.markdown(
            """
            Welcome to the Micro-Cap Portfolio Manager! Here's how to use the app:

            1. **Initial Setup**
               * Add cash to your account using the Cash Balance section
               * Use the Buy form to make your first purchase

            2. **Managing Your Portfolio**
               * Monitor your holdings in the Portfolio section
               * Use Stop Loss settings to manage risk
               * Track performance metrics in real-time

            3. **Trading**
               * Buy stocks using the Buy form
               * Sell positions using the Sell form
               * Monitor your cash balance

            4. **Watchlist**
               * Add stocks to your watchlist
               * Track potential investments
               * Monitor price changes
            """
        )

        st.subheader("Risk Management")
        st.markdown(
            """
            * Set stop losses for each position
            * Monitor total portfolio exposure
            * Track individual position sizes
            """
        )
