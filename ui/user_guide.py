import streamlit as st


def render_user_guide() -> None:
    st.markdown(
        """
        ### Navigation
        - The top bar links to **Dashboard**, **Performance**, and **User Guide**.
        - Use **Download Portfolio** to grab a CSV snapshot of your current holdings.

        ### Getting Started
        1. On first load an onboarding tip box explains that data lives in the local `data/` folder. Click **Dismiss** to hide it.
        2. **Set a starting cash balance.** The dashboard prompts for initial cash to trade with.
        3. **Maintain a watchlist.** Use the sidebar lookup to search for tickers and add them with **Add to Watchlist**.
        4. Refresh watchlist prices with the 🔄 icon next to the *Watchlist* header and remove symbols using the ❌ button.

        ### Buying Stocks
        1. Open the *Log a Buy* form.
        2. Enter the ticker symbol, number of shares, and the price you paid.
        3. Provide a **Stop Loss %**. For example, entering `10` sets a stop price 10% below your purchase price. The app stores the calculated price for you.

        ### Selling Stocks
        - Once you hold a position it appears in the *Current Portfolio* table. Use the *Log a Sell* form to close or trim a position.

        ### Current Portfolio Table
        - Shows each holding with buy price, current price, stop loss and unrealised profit or loss. Refresh prices manually or enable auto-refresh for updates every 30 minutes.

        ### Performance Dashboard
        - View your equity curve over a selectable date range and a summary of metrics: Total Return, Net Profit, Initial Equity, Final Equity, Max Drawdown, Number of Trading Days, Average Daily Return, Volatility, and Sharpe Ratio.

        ### Daily Summary
        - Use the *Generate Daily Summary* button to create a markdown snapshot of your portfolio and watchlist for easy sharing or journaling.

        ### Tips
        - Add extra funds at any time using the *Add Cash* button under **Cash Balance**.
        - Stop losses are stored as dollar prices even though you input a percentage.
        - The app saves data to the local `data/` folder so you can pick up where you left off.
        """
    )
