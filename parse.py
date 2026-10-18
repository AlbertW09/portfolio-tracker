import pandas as pd


def clean_number(column):
    text = column.astype(str).str.replace("[$,+%]", "", regex=True)
    return pd.to_numeric(text, errors="coerce")


def load_positions(path):
    df = pd.read_csv(path, index_col=False, encoding="utf-8-sig")

    df.columns = df.columns.str.strip().str.lower()

    df = df.rename(columns={
        "account name": "account",
        "symbol": "symbol",
        "description": "description",
        "quantity": "quantity",
        "last price": "last_price",
        "current value": "current_value",
        "cost basis total": "cost_basis",
    })
    df = df[["account", "symbol", "description", "quantity",
             "last_price", "current_value", "cost_basis"]].copy()

    df = df[df["symbol"].notna()]

    for col in ["quantity", "last_price", "current_value", "cost_basis"]:
        df[col] = clean_number(df[col])

    is_cash = df["symbol"].str.endswith("**") | (df["symbol"] == "Pending Activity")
    df.loc[is_cash, "symbol"] = df.loc[is_cash, "symbol"].str.replace("**", "")
    df.loc[is_cash, "quantity"] = df.loc[is_cash, "current_value"]
    df.loc[is_cash, "last_price"] = 1.0
    df.loc[is_cash, "cost_basis"] = df.loc[is_cash, "current_value"]
    df["is_cash"] = is_cash

    return df.reset_index(drop=True)
