import pandas as pd
import yfinance as yf


def get_prices(symbols):
    tickers = [s.replace(".", "-") for s in symbols]
    data = yf.download(tickers, period="5d", progress=False, auto_adjust=False)
    latest = data["Close"].ffill().iloc[-1]

    prices = {}
    for symbol, ticker in zip(symbols, tickers):
        if ticker in latest and pd.notna(latest[ticker]):
            prices[symbol] = float(latest[ticker])
    return prices


def add_live_values(df):
    df = df.copy()
    stock_symbols = df.loc[~df["is_cash"], "symbol"].unique().tolist()
    live = get_prices(stock_symbols)

    df["price"] = df["symbol"].map(live).fillna(df["last_price"])
    df.loc[df["is_cash"], "price"] = 1.0
    df["value"] = df["quantity"] * df["price"]
    df["gain"] = df["value"] - df["cost_basis"]
    df["gain_pct"] = df["gain"] / df["cost_basis"] * 100
    return df