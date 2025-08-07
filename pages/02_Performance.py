import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from components.nav import navbar
from ui.watchlist import show_watchlist_sidebar


st.set_page_config(page_title="Performance", layout="wide", initial_sidebar_state="collapsed")

navbar(Path(__file__).name)

show_watchlist_sidebar()

st.subheader("Performance Dashboard")

@st.cache_data
def load_portfolio_history(db_path: str) -> pd.DataFrame:
    """Load total equity history from the portfolio database."""
    conn = sqlite3.connect(db_path)
    query = (
        "SELECT date AS Date, total_equity AS Total_Equity "
        "FROM portfolio_history WHERE ticker='TOTAL' ORDER BY date;"
    )
    df = pd.read_sql_query(query, conn, parse_dates=["Date"])
    conn.close()
    df["Total_Equity"] = df["Total_Equity"].astype(float)
    return df


def main() -> None:
    db_path = Path(__file__).resolve().parent.parent / "data" / "trading.db"
    history = load_portfolio_history(str(db_path))

    min_date = history["Date"].min().date()
    max_date = history["Date"].max().date()
    start_date, end_date = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    mask = (history["Date"] >= pd.to_datetime(start_date)) & (
        history["Date"] <= pd.to_datetime(end_date)
    )
    hist_filtered = history.loc[mask]

    col_chart, col_meta = st.columns([2, 1])

    with col_chart:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(
            hist_filtered["Date"],
            hist_filtered["Total_Equity"],
            marker="o",
            label="Portfolio",
        )
        ax.set_xlabel("Date")
        ax.set_ylabel("Equity")
        ax.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(fig, use_container_width=True)

    if hist_filtered.shape[0] < 2:
        st.warning("Not enough data available for selected date range.")
        return

    initial_equity = hist_filtered["Total_Equity"].iloc[0]
    final_equity = hist_filtered["Total_Equity"].iloc[-1]
    net_profit = final_equity - initial_equity
    total_return = (final_equity / initial_equity - 1) * 100
    daily_returns = hist_filtered["Total_Equity"].pct_change().dropna()
    avg_daily_return = daily_returns.mean() * 100
    volatility = daily_returns.std() * 100
    sharpe_ratio = (
        (daily_returns.mean() / daily_returns.std()) * (252 ** 0.5)
        if not daily_returns.empty and daily_returns.std() != 0
        else 0
    )
    roll_max = hist_filtered["Total_Equity"].cummax()
    drawdown = hist_filtered["Total_Equity"] / roll_max - 1
    max_drawdown = drawdown.min() * 100
    num_days = hist_filtered.shape[0]

    with col_meta:
        st.subheader("Performance Summary")
        st.metric("Total Return (%)", f"{total_return:.2f}%")
        st.metric("Net Profit ($)", f"${net_profit:,.2f}")
        st.metric("Initial Equity", f"${initial_equity:,.2f}")
        st.metric("Final Equity", f"${final_equity:,.2f}")
        st.metric("Max Drawdown (%)", f"{max_drawdown:.2f}%")
        st.metric("Number of Trading Days", f"{num_days}")
        st.metric("Average Daily Return (%)", f"{avg_daily_return:.2f}%")
        st.metric("Volatility (%)", f"{volatility:.2f}%")
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")


if __name__ == "__main__":
    main()

