import pandas as pd


def clean_currency(val):
  if pd.isna(val) or str(val).strip().lower() in ["n/a", "", "--"]:
    return 0.0

  val_str = (
      str(val).replace("$", "").replace(",", "").replace("+", "").strip()
  )

  if val_str.endswith("%"):
    try:
      return float(val_str[:-1]) / 100.0
    except ValueError:
      return 0.0

  try:
    return float(val_str)
  except ValueError:
    return 0.0


def load_positions(path):
  df = pd.read_csv(path, skipfooter=5, engine="python", on_bad_lines="skip")
  df.columns = df.columns.str.strip()
  df = df.loc[:, ~df.columns.duplicated()]

  symbol_col = df.columns[0]
  df = df.dropna(subset=[symbol_col])

  col_mapping = {}
  used_targets = set()
  for col in df.columns:
    c_lower = col.lower()
    target = None
    if "symbol" in c_lower and "symbol" not in used_targets:
      target = "symbol"
    elif "description" in c_lower and "description" not in used_targets:
      target = "description"
    elif "quantity" in c_lower and "quantity" not in used_targets:
      target = "quantity"
    elif "price" in c_lower and "last_price" not in used_targets:
      target = "last_price"
    elif "current value" in c_lower and "current_value" not in used_targets:
      target = "current_value"
    elif "cost basis" in c_lower and "cost_basis" not in used_targets:
      target = "cost_basis"

    if target:
      col_mapping[col] = target
      used_targets.add(target)

  df = df.rename(columns=col_mapping)

  required_cols = [
      "symbol",
      "description",
      "quantity",
      "last_price",
      "current_value",
      "cost_basis",
  ]
  df = df[[c for c in required_cols if c in df.columns]]

  numeric_cols = ["quantity", "last_price", "current_value", "cost_basis"]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = df[col].apply(clean_currency)

  if "symbol" in df.columns and "current_value" in df.columns:
    spaxx_mask = df["symbol"].str.contains("SPAXX", na=False)

    df.loc[spaxx_mask & (df["quantity"] == 0.0), "quantity"] = df.loc[
        spaxx_mask, "current_value"
    ]
    df.loc[spaxx_mask & (df["last_price"] == 0.0), "last_price"] = 1.0
    df.loc[spaxx_mask & (df["cost_basis"] == 0.0), "cost_basis"] = df.loc[
        spaxx_mask, "current_value"
    ]

  return df