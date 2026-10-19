from parse import load_positions
from prices import add_live_values
from compare import spy_value_today

df = load_positions(r"C:\Users\awcod\Downloads\Portfolio_Positions_Oct-18-2026.csv")
df = add_live_values(df)

print(df[["symbol", "quantity", "price", "value", "cost_basis", "gain", "gain_pct"]].round(2).to_string(index=False))

invested = df[~df["is_cash"] & df["cost_basis"].notna()]
total_value = df["value"].sum()
total_gain = invested["gain"].sum()
total_cost = invested["cost_basis"].sum()

print()
print(f"Fidelity's total: ${df['current_value'].sum():,.2f}")
print(f"Live total:       ${df['value'].sum():,.2f}")
print(f"Total gain:   ${total_gain:,.2f} ({total_gain / total_cost * 100:.2f}%)")

###
put_in = sum(amount for date, amount in deposits)
my_value = df["value"].sum()
spy_value = spy_value_today(deposits)

print()
print(f"Money put in:        ${put_in:,.2f}")
print(f"My portfolio today:  ${my_value:,.2f}  ({(my_value / put_in - 1) * 100:+.2f}%)")
print(f"If all in S&P 500:   ${spy_value:,.2f}  ({(spy_value / put_in - 1) * 100:+.2f}%)")
print(f"Difference:          ${my_value - spy_value:+,.2f}")