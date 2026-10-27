import datetime as dt

import pandas as pd


def add_today(history_file, value):
    if history_file is None:
        history = pd.DataFrame({"date": pd.Series(dtype="datetime64[ns]"), "value": pd.Series(dtype=float)})
    else:
        history = pd.read_csv(history_file, parse_dates=["date"])

    today = pd.Timestamp(dt.date.today())
    history = history[history["date"] != today]
    today_row = pd.DataFrame({"date": [today], "value": [value]})
    history = pd.concat([history, today_row])

    return history.sort_values("date").reset_index(drop=True)