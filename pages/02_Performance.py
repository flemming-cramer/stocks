import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf

from components.nav import navbar


st.set_page_config(page_title="Performance", layout="wide", initial_sidebar_state="expanded")

navbar(Path(__file__).name)

st.title("📈 Performance Dashboard")


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


@st.cache_data
def load_spx(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Download and normalize S&P 500 index data."""
    data = yf.download("^SPX", start=start, end=end + pd.Timedelta(days=1))
    data = data.reset_index()[["Date", "Close"]]
    data["SPX_Equity"] = data["Close"] / data["Close"].iloc[0] * 100
    return data


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
    show_benchmark = st.checkbox("Show S&P 500 benchmark", value=True)

    mask = (history["Date"] >= pd.to_datetime(start_date)) & (
        history["Date"] <= pd.to_datetime(end_date)
    )
    hist_filtered = history.loc[mask]

    fig, ax = plt.subplots()
    ax.plot(
        hist_filtered["Date"],
        hist_filtered["Total_Equity"],
        marker="o",
        label="Portfolio",
    )

    if show_benchmark:
        spx = load_spx(pd.to_datetime(start_date), pd.to_datetime(end_date))
        spx_filtered = spx[
            (spx["Date"] >= pd.to_datetime(start_date))
            & (spx["Date"] <= pd.to_datetime(end_date))
        ]
        ax.plot(
            spx_filtered["Date"], spx_filtered["SPX_Equity"], marker="o", label="S&P 500"
        )

    ax.set_xlabel("Date")
    ax.set_ylabel("Equity")
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)

    st.pyplot(fig)

    total_return = (
        hist_filtered["Total_Equity"].iloc[-1] / hist_filtered["Total_Equity"].iloc[0] - 1
    ) * 100
    st.metric("Total Return", f"{total_return:.2f}%")


if __name__ == "__main__":
    main()

