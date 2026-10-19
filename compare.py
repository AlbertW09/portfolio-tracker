import pandas as pd
import yfinance as yf


def spy_value_today(deposits):
    first_date = min(date for date, amount in deposits)
    spy = yf.download("SPY", start=first_date, progress=False, auto_adjust=True)["Close"].squeeze()
    #print(spy)
    shares = 0
    for date, amount in deposits:
        price = spy[spy.index >= pd.Timestamp(date)].iloc[0]
        shares += amount / price

    return shares * spy.iloc[-1]