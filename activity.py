import pandas as pd

from parse import clean_number
from prices import price_history


def load_activity(path):
    df = pd.read_csv(path, index_col=False, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    # bottom of the file is disclaimer text, which won't read as a date, so this drops it
    df["date"] = pd.to_datetime(df["Run Date"].str.strip(), format="%m/%d/%Y", errors="coerce")
    df = df[df["date"].notna()].copy()

    df["action"] = df["Action"].str.upper()
    df["symbol"] = df["Symbol"].str.strip()
    df["quantity"] = clean_number(df["Quantity"]).fillna(0)
    df["amount"] = clean_number(df["Amount ($)"]).fillna(0)
    return df[["date", "action", "symbol", "quantity", "amount"]]


def get_deposits(activity):
    is_deposit = activity["action"].str.contains("CONTRIBUTION|ELECTRONIC FUNDS TRANSFER")
    deposits = activity[is_deposit]
    return list(zip(deposits["date"], deposits["amount"]))


def portfolio_history(activity, cash_symbols):
    days = pd.date_range(activity["date"].min(), pd.Timestamp.today().normalize())

    cash = activity.groupby("date")["amount"].sum().cumsum()
    cash = cash.reindex(days).ffill()

    trades = activity[activity["quantity"] != 0]
    shares = trades.pivot_table(index="date", columns="symbol", values="quantity",
                                aggfunc="sum", fill_value=0).cumsum()
    shares = shares.reindex(days).ffill().fillna(0)

    stocks = [s for s in shares.columns if s not in cash_symbols]
    prices = price_history(stocks, days[0])
    trading_days = prices.index
    # weekends and holidays have no price, so they use the last day's close
    prices = prices.reindex(days).ffill()

    # money market funds like SPAXX are always worth $1 a share
    for symbol in shares.columns:
        if symbol in cash_symbols:
            prices[symbol] = 1.0

    value = (shares * prices).sum(axis=1) + cash
    return value[value.index.isin(trading_days)]
