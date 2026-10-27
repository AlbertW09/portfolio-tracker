import pandas as pd
import yfinance as yf


def spy_history(deposits):
    first_date = min(date for date, amount in deposits)
    start = pd.Timestamp(first_date) - pd.Timedelta(days=7)
    spy = yf.download("SPY", start=start, progress=False, auto_adjust=True)["Close"].squeeze()

    shares = pd.Series(0.0, index=spy.index)
    put_in = pd.Series(0.0, index=spy.index)
    for date, amount in deposits:
        after = spy.index >= pd.Timestamp(date)
        if not after.any():
            after = spy.index == spy.index[-1]
        price = spy[after].iloc[0]
        shares[after] += amount / price
        put_in[after] += amount

    history = pd.DataFrame({"spy_value": shares * spy, "put_in": put_in})
    return history[history["put_in"] > 0]