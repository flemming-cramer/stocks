# Improved user prompts and guidance for manual trades and daily summaries
# (2025-08-04 usability update)
"""Utilities for maintaining the ChatGPT micro cap portfolio.

The script processes portfolio positions, logs trades, and prints daily
results. It is intentionally lightweight and avoids changing existing
logic or behaviour.
"""

from datetime import datetime
from pathlib import Path

import logging
import numpy as np
import pandas as pd
import yfinance as yf
from typing import Any, cast
import os
import time

# Shared file locations
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR  # Save files in the same folder as this script
PORTFOLIO_CSV = DATA_DIR / "chatgpt_portfolio_update.csv"
TRADE_LOG_CSV = DATA_DIR / "chatgpt_trade_log.csv"


logger = logging.getLogger(__name__)


def configure_logger(level: int = logging.INFO) -> None:
    """Configure module-level logging."""
    logging.basicConfig(level=level)


def set_data_dir(data_dir: Path) -> None:
    """Update global paths for portfolio and trade logs.

    Parameters
    ----------
    data_dir:
        Directory where ``chatgpt_portfolio_update.csv`` and
        ``chatgpt_trade_log.csv`` are stored.
    """

    global DATA_DIR, PORTFOLIO_CSV, TRADE_LOG_CSV
    DATA_DIR = Path(data_dir)
    os.makedirs(DATA_DIR, exist_ok=True)
    PORTFOLIO_CSV = DATA_DIR / "chatgpt_portfolio_update.csv"
    TRADE_LOG_CSV = DATA_DIR / "chatgpt_trade_log.csv"

# Today's date reused across logs
today = datetime.today().strftime("%Y-%m-%d")
now = datetime.now()
day = now.weekday()



def process_portfolio(
    portfolio: pd.DataFrame | dict[str, list[object]] | list[dict[str, object]],
    cash: float,
) -> tuple[pd.DataFrame, float]:
    """Update daily price information, log stop-loss sells, and prompt for trades."""

    portfolio_df = _to_dataframe(portfolio)
    _confirm_weekend()
    portfolio_df, cash = _prompt_trade_actions(portfolio_df, cash)
    results, total_value, total_pnl, portfolio_df, cash = _update_positions(portfolio_df, cash)
    _log_daily_totals(total_value, total_pnl, cash)
    _save_daily_results(results)
    return portfolio_df, cash


def _to_dataframe(
    portfolio: pd.DataFrame | dict[str, list[object]] | list[dict[str, object]]
) -> pd.DataFrame:
    """Normalise portfolio input to a DataFrame."""
    if isinstance(portfolio, pd.DataFrame):
        return portfolio.copy()
    if isinstance(portfolio, (dict, list)):
        return pd.DataFrame(portfolio)
    raise TypeError("portfolio must be a DataFrame, dict, or list of dicts")


def _confirm_weekend() -> None:
    """Prompt user confirmation if run on a weekend."""
    if day in {5, 6}:
        check = input(
            """Today is currently a weekend, so markets were never open.
This will cause the program to calculate data from the last day (usually Friday), and save it as today.
Are you sure you want to do this? To exit, enter 1. """
        )
        if check == "1":
            raise SystemError("Exitting program...")


def _prompt_trade_actions(portfolio_df: pd.DataFrame, cash: float) -> tuple[pd.DataFrame, float]:
    """Handle manual buy/sell prompts from the user."""
    while True:
        action = input(
            f"""You have ${cash:.2f} in cash.
Would you like to buy or sell a stock today?
Type 'b' to buy, 's' to sell, or press Enter to skip: """
        ).strip().lower()
        if action == "b":
            try:
                ticker = input("What is the stock's ticker symbol (e.g. PLTR)? ").strip().upper()
                shares = float(input("How many shares do you want to buy? "))
                buy_price = float(input("At what price per share do you want to buy it? "))
                stop_loss = float(
                    input(
                        "Set your stop-loss price (the price where you'll sell to limit loss): "
                    )
                )
                if shares <= 0 or buy_price <= 0 or stop_loss <= 0:
                    raise ValueError
            except ValueError:
                logger.warning("Invalid input. Manual buy cancelled.")
            else:
                cash, portfolio_df = log_manual_buy(buy_price, shares, ticker, stop_loss, cash, portfolio_df)
            continue
        if action == "s":
            try:
                ticker = input("What is the stock's ticker symbol (e.g. PLTR)? ").strip().upper()
                shares = float(input("How many shares do you want to sell? "))
                sell_price = float(input("At what price per share do you want to sell it? "))
                if shares <= 0 or sell_price <= 0:
                    raise ValueError
            except ValueError:
                logger.warning("Invalid input. Manual sell cancelled.")
            else:
                cash, portfolio_df = log_manual_sell(sell_price, shares, ticker, cash, portfolio_df)
            continue
        break
    return portfolio_df, cash


def _update_positions(portfolio_df: pd.DataFrame, cash: float) -> tuple[list[dict[str, object]], float, float, pd.DataFrame, float]:
    """Update portfolio positions with latest market data."""
    results: list[dict[str, object]] = []
    total_value = 0.0
    total_pnl = 0.0
    for _, stock in portfolio_df.iterrows():
        ticker = stock["ticker"]
        shares = int(stock["shares"])
        cost = stock["buy_price"]
        stop = stock["stop_loss"]
        data = yf.Ticker(ticker).history(period="1d")
        if data.empty:
            logger.warning("No data for %s", ticker)
            row = {
                "Date": today,
                "Ticker": ticker,
                "Shares": shares,
                "Cost Basis": cost,
                "Stop Loss": stop,
                "Current Price": "",
                "Total Value": "",
                "PnL": "",
                "Action": "NO DATA",
                "Cash Balance": "",
                "Total Equity": "",
            }
        else:
            low_price = round(float(data["Low"].iloc[-1]), 2)
            close_price = round(float(data["Close"].iloc[-1]), 2)
            if low_price <= stop:
                price = stop
                value = round(price * shares, 2)
                pnl = round((price - cost) * shares, 2)
                action = "SELL - Stop Loss Triggered"
                cash += value
                portfolio_df = log_sell(ticker, shares, price, cost, pnl, portfolio_df)
                logger.info(
                    "🔻 Stop-loss triggered: Sold %s shares of %s at $%s (Buy price was $%s)
You lost $%s on this position.",
                    shares,
                    ticker,
                    price,
                    cost,
                    -pnl,
                )
            else:
                price = close_price
                value = round(price * shares, 2)
                pnl = round((price - cost) * shares, 2)
                action = "HOLD"
                total_value += value
                total_pnl += pnl
                logger.info(
                    "✅ Holding %s — Current price: $%s | PnL: $%s",
                    ticker,
                    price,
                    pnl,
                )
            row = {
                "Date": today,
                "Ticker": ticker,
                "Shares": shares,
                "Cost Basis": cost,
                "Stop Loss": stop,
                "Current Price": price,
                "Total Value": value,
                "PnL": pnl,
                "Action": action,
                "Cash Balance": "",
                "Total Equity": "",
            }
        results.append(row)
    total_row = {
        "Date": today,
        "Ticker": "TOTAL",
        "Shares": "",
        "Cost Basis": "",
        "Stop Loss": "",
        "Current Price": "",
        "Total Value": round(total_value, 2),
        "PnL": round(total_pnl, 2),
        "Action": "",
        "Cash Balance": round(cash, 2),
        "Total Equity": round(total_value + cash, 2),
    }
    results.append(total_row)
    return results, total_value, total_pnl, portfolio_df, cash


def _log_daily_totals(total_value: float, total_pnl: float, cash: float) -> None:
    """Log the day's portfolio totals."""
    logger.info(
        "
Today's totals:
- Total stock value: $%s
- Total PnL: $%s
- Cash balance: $%s
- Total equity: $%s
",
        round(total_value, 2),
        round(total_pnl, 2),
        round(cash, 2),
        round(total_value + cash, 2),
    )


def _save_daily_results(results: list[dict[str, object]]) -> None:
    """Persist daily portfolio results to CSV."""
    df = pd.DataFrame(results)
    if PORTFOLIO_CSV.exists():
        existing = pd.read_csv(PORTFOLIO_CSV)
        existing = existing[existing["Date"] != today]
        logger.info("rows for today already logged, not saving results to CSV...")
        time.sleep(1)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(PORTFOLIO_CSV, index=False)



def log_sell(
    ticker: str,
    shares: float,
    price: float,
    cost: float,
    pnl: float,
    portfolio: pd.DataFrame,
) -> pd.DataFrame:
    """Record a stop-loss sale in ``TRADE_LOG_CSV`` and remove the ticker."""
    log = {
        "Date": today,
        "Ticker": ticker,
        "Shares Sold": shares,
        "Sell Price": price,
        "Cost Basis": cost,
        "PnL": pnl,
        "Reason": "AUTOMATED SELL - STOPLOSS TRIGGERED",
    }

    portfolio = portfolio[portfolio["ticker"] != ticker]

    if TRADE_LOG_CSV.exists():
        df = pd.read_csv(TRADE_LOG_CSV)
        df = pd.concat([df, pd.DataFrame([log])], ignore_index=True)
    else:
        df = pd.DataFrame([log])
    df.to_csv(TRADE_LOG_CSV, index=False)
    return portfolio


def log_manual_buy(
    buy_price: float,
    shares: float,
    ticker: str,
    stoploss: float,
    cash: float,
    chatgpt_portfolio: pd.DataFrame,
) -> tuple[float, pd.DataFrame]:
    """Log a manual purchase and append to the portfolio."""
    check = input(
        f"You’re about to buy {shares} shares of {ticker} at ${buy_price} with a stop-loss at ${stoploss}.\n"
        "Type 1 to cancel, or press Enter to confirm: "
    )
    if check == "1":
        logger.info("Returning...")
        return cash, chatgpt_portfolio

    data = yf.download(ticker, period="1d")
    data = cast(pd.DataFrame, data)
    if data.empty:
        logger.warning("Manual buy for %s failed: no market data available.", ticker)
        return cash, chatgpt_portfolio
    day_high = float(data["High"].iloc[-1].item())
    day_low = float(data["Low"].iloc[-1].item())
    if not (day_low <= buy_price <= day_high):
        logger.warning(
            "Manual buy for %s at %s failed: price outside today's range %s-%s.",
            ticker,
            buy_price,
            round(day_low, 2),
            round(day_high, 2),
        )
        return cash, chatgpt_portfolio
    if buy_price * shares > cash:
        logger.warning(
            "Manual buy for %s failed: cost %s exceeds cash balance %s.",
            ticker,
            buy_price * shares,
            cash,
        )
        return cash, chatgpt_portfolio
    pnl = 0.0

    log = {
        "Date": today,
        "Ticker": ticker,
        "Shares Bought": shares,
        "Buy Price": buy_price,
        "Cost Basis": buy_price * shares,
        "PnL": pnl,
        "Reason": "MANUAL BUY - New position",
    }

    if os.path.exists(TRADE_LOG_CSV):
        df = pd.read_csv(TRADE_LOG_CSV)
        df = pd.concat([df, pd.DataFrame([log])], ignore_index=True)
    else:
        df = pd.DataFrame([log])
    df.to_csv(TRADE_LOG_CSV, index=False)
    # if the portfolio doesn't already contain ticker, create a new row.
    
    mask = chatgpt_portfolio["ticker"] == ticker

    if not mask.any():
        new_trade = {
            "ticker": ticker,
            "shares": shares,
            "stop_loss": stoploss,
            "buy_price": buy_price,
            "cost_basis": buy_price * shares,
        }
        chatgpt_portfolio = pd.concat(
            [chatgpt_portfolio, pd.DataFrame([new_trade])], ignore_index=True
        )
    else:
        row_index = chatgpt_portfolio[mask].index[0]
        current_shares = float(chatgpt_portfolio.at[row_index, "shares"])
        chatgpt_portfolio.at[row_index, "shares"] = current_shares + shares
        current_cost_basis = float(chatgpt_portfolio.at[row_index, "cost_basis"])
        chatgpt_portfolio.at[row_index, "cost_basis"] = shares * buy_price + current_cost_basis
        chatgpt_portfolio.at[row_index, "stop_loss"] = stoploss
    cash = cash - shares * buy_price
    logger.info("Manual buy for %s complete!", ticker)
    return cash, chatgpt_portfolio


def log_manual_sell(
    sell_price: float,
    shares_sold: float,
    ticker: str,
    cash: float,
    chatgpt_portfolio: pd.DataFrame,
) -> tuple[float, pd.DataFrame]:
    """Log a manual sale and update the portfolio."""
    reason = input(
        f"You’re about to sell {shares_sold} shares of {ticker} at ${sell_price}.\n"
        "Enter your reason for selling, or type 1 to cancel: "
    )

    if reason == "1":
        logger.info("Returning...")
        return cash, chatgpt_portfolio
    if ticker not in chatgpt_portfolio["ticker"].values:
        logger.warning("Manual sell for %s failed: ticker not in portfolio.", ticker)
        return cash, chatgpt_portfolio
    ticker_row = chatgpt_portfolio[chatgpt_portfolio["ticker"] == ticker]

    total_shares = int(ticker_row["shares"].item())
    if shares_sold > total_shares:
        logger.warning(
            "Manual sell for %s failed: trying to sell %s shares but only own %s.",
            ticker,
            shares_sold,
            total_shares,
        )
        return cash, chatgpt_portfolio
    data = yf.download(ticker, period="1d")
    data = cast(pd.DataFrame, data)
    if data.empty:
        logger.warning("Manual sell for %s failed: no market data available.", ticker)
        return cash, chatgpt_portfolio
    day_high = float(data["High"].iloc[-1])
    day_low = float(data["Low"].iloc[-1])
    if not (day_low <= sell_price <= day_high):
        logger.warning(
            "Manual sell for %s at %s failed: price outside today's range %s-%s.",
            ticker,
            sell_price,
            round(day_low, 2),
            round(day_high, 2),
        )
        return cash, chatgpt_portfolio
    buy_price = float(ticker_row["buy_price"].item())
    cost_basis = buy_price * shares_sold
    pnl = sell_price * shares_sold - cost_basis
    log = {
        "Date": today,
        "Ticker": ticker,
        "Shares Bought": "",
        "Buy Price": "",
        "Cost Basis": cost_basis,
        "PnL": pnl,
        "Reason": f"MANUAL SELL - {reason}",
        "Shares Sold": shares_sold,
        "Sell Price": sell_price,
    }
    if os.path.exists(TRADE_LOG_CSV):
        df = pd.read_csv(TRADE_LOG_CSV)
        df = pd.concat([df, pd.DataFrame([log])], ignore_index=True)
    else:
        df = pd.DataFrame([log])
    df.to_csv(TRADE_LOG_CSV, index=False)

    if total_shares == shares_sold:
        chatgpt_portfolio = chatgpt_portfolio[chatgpt_portfolio["ticker"] != ticker]
    else:
        row_index = ticker_row.index[0]
        chatgpt_portfolio.at[row_index, "shares"] = total_shares - shares_sold
        chatgpt_portfolio.at[row_index, "cost_basis"] = (
            chatgpt_portfolio.at[row_index, "shares"]
            * chatgpt_portfolio.at[row_index, "buy_price"]
        )

    cash = cash + shares_sold * sell_price
    logger.info("manual sell for %s complete!", ticker)
    return cash, chatgpt_portfolio


def daily_results(chatgpt_portfolio: pd.DataFrame, cash: float) -> None:
    """Print daily price updates and performance metrics."""
    portfolio_dict: list[dict[str, object]] = chatgpt_portfolio.to_dict(orient="records")

    logger.info("prices and updates for %s", today)
    time.sleep(1)
    for stock in portfolio_dict + [{"ticker": "^RUT"}] + [{"ticker": "IWO"}] + [{"ticker": "XBI"}]:
        ticker = stock["ticker"]
        try:
            data = yf.download(ticker, period="2d", progress=False)
            data = cast(pd.DataFrame, data)
            if data.empty or len(data) < 2:
                logger.warning("Data for %s was empty or incomplete.", ticker)
                continue
            price = float(data["Close"].iloc[-1].item())
            last_price = float(data["Close"].iloc[-2].item())

            percent_change = ((price - last_price) / last_price) * 100
            volume = float(data["Volume"].iloc[-1].item())
        except Exception as e:
            raise Exception(f"Download for {ticker} failed. {e} Try checking internet connection.")
        logger.info("%s closing price: %.2f", ticker, price)
        logger.info("%s volume for today: $%s", ticker, f"{volume:,}")
        logger.info("percent change from the day before: %.2f%%", percent_change)
    chatgpt_df = pd.read_csv(PORTFOLIO_CSV)

    # Filter TOTAL rows and get latest equity
    chatgpt_totals = chatgpt_df[chatgpt_df["Ticker"] == "TOTAL"].copy()
    chatgpt_totals["Date"] = pd.to_datetime(chatgpt_totals["Date"])
    final_date = chatgpt_totals["Date"].max()
    final_value = chatgpt_totals[chatgpt_totals["Date"] == final_date]
    final_equity = float(final_value["Total Equity"].values[0])
    equity_series = chatgpt_totals["Total Equity"].astype(float).reset_index(drop=True)

    # Daily returns
    daily_pct = equity_series.pct_change().dropna()

    total_return = (equity_series.iloc[-1] - equity_series.iloc[0]) / equity_series.iloc[0] 

    # Number of total trading days
    n_days = len(chatgpt_totals)
    # Risk-free return over total trading period (assuming 4.5% risk-free rate)
    rf_annual = 0.045
    rf_period = (1 + rf_annual) ** (n_days / 252) - 1
    # Standard deviation of daily returns
    std_daily = daily_pct.std()
    negative_pct = daily_pct[daily_pct < 0]
    negative_std = negative_pct.std()
    # Sharpe Ratio
    sharpe_total = (total_return - rf_period) / (std_daily * np.sqrt(n_days))
    # Sortino Ratio
    sortino_total = (total_return - rf_period) / (negative_std * np.sqrt(n_days))

    # Output
    logger.info("Total Sharpe Ratio over %s days: %.4f", n_days, sharpe_total)
    logger.info("Total Sortino Ratio over %s days: %.4f", n_days, sortino_total)
    logger.info("Latest ChatGPT Equity: $%.2f", final_equity)
    # Get S&P 500 data
    spx = yf.download("^SPX", start="2025-06-27", end=final_date + pd.Timedelta(days=1), progress=False)
    spx = cast(pd.DataFrame, spx)
    spx = spx.reset_index()

    # Normalize to $100
    initial_price = spx["Close"].iloc[0].item()
    price_now = spx["Close"].iloc[-1].item()
    scaling_factor = 100 / initial_price
    spx_value = price_now * scaling_factor
    logger.info("$100 Invested in the S&P 500: $%.2f", spx_value)
    logger.info("today's portfolio:")
    logger.info("%s", chatgpt_portfolio)
    logger.info("cash balance: %s", cash)

    logger.info(
        "Here is your update for today. You can make any changes you see fit (if necessary),\n"
        "but you may not use deep research. You do have to ask permissons for any changes, as you have full control.\n"
        "You can however use the Internet and check current prices for potenial buys."
    )


def main(file: str, data_dir: Path | None = None) -> None:
    """Run the trading script.

    Parameters
    ----------
    file:
        CSV file containing historical portfolio records.
    data_dir:
        Directory where trade and portfolio CSVs will be stored.
    """
    configure_logger()
    chatgpt_portfolio, cash = load_latest_portfolio_state(file)
    if data_dir is not None:
        set_data_dir(data_dir)

    chatgpt_portfolio, cash = process_portfolio(chatgpt_portfolio, cash)
    daily_results(chatgpt_portfolio, cash)

def load_latest_portfolio_state(
    file: str,
) -> tuple[pd.DataFrame, float]:
    """Load the most recent portfolio snapshot and cash balance.

    Parameters
    ----------
    file:
        CSV file containing historical portfolio records.

    Returns
    -------
    tuple[pd.DataFrame, float]
        A DataFrame of holdings and the current cash balance.
    """
    df = pd.read_csv(file)
    
    # If no data exists, return initialized empty portfolio and prompt for cash
    if df.empty:
        logger.info("Portfolio CSV is empty. Returning set amount of cash for creating portfolio.")
        try:
            cash = float(input("What would you like your starting cash amount to be? "))
        except ValueError:
            raise ValueError("Cash could not be converted to float datatype. Please enter a valid number.")
        
        # Define an empty portfolio with correct columns
        portfolio = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
        return portfolio, cash

    # Separate out all rows that are not TOTAL summary rows
    non_total = df[df["Ticker"] != "TOTAL"].copy()
    non_total["Date"] = pd.to_datetime(non_total["Date"])

    if non_total.empty:
        portfolio = pd.DataFrame(columns=["ticker", "shares", "stop_loss", "buy_price", "cost_basis"])
    else:
        latest_date = non_total["Date"].max()
        latest_tickers = non_total[non_total["Date"] == latest_date].copy()

        latest_tickers.drop(columns=["Date", "Cash Balance", "Total Equity", "Action", "Current Price", "PnL", "Total Value"], inplace=True)
        latest_tickers.rename(columns={
            "Ticker": "ticker",
            "Shares": "shares",
            "Stop Loss": "stop_loss",
            "Cost Basis": "buy_price"
        }, inplace=True)
        latest_tickers["cost_basis"] = latest_tickers["shares"] * latest_tickers["buy_price"]
        portfolio = latest_tickers.reset_index(drop=True)

    df = df[df["Ticker"] == "TOTAL"].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    latest = df.sort_values("Date").iloc[-1]
    cash = float(latest["Cash Balance"])

    return portfolio, cash


