import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from activity import get_deposits, load_activity, portfolio_history
from compare import spy_history
from parse import load_positions
from prices import add_live_values

st.set_page_config(page_title="Portfolio Tracker", layout="wide")
st.title("Portfolio Tracker")

positions_file = st.file_uploader("Upload your Fidelity positions CSV (Positions page → Download)", type="csv")
activity_file = st.file_uploader("Upload your Fidelity activity CSV (Activity & Orders page → Download)", type="csv")

if positions_file is None or activity_file is None:
    st.info("Upload both files to get started.")
    st.stop()

df = load_positions(positions_file)
df = add_live_values(df)
my_value = df["value"].sum()

activity = load_activity(activity_file)
deposits = get_deposits(activity)
if not deposits:
    st.error("Couldn't find any deposits in your activity file.")
    st.stop()

cash_symbols = set(df.loc[df["is_cash"], "symbol"])
my_history = portfolio_history(activity, cash_symbols)

put_in = sum(amount for date, amount in deposits)
spy = spy_history(deposits)
spy_value = spy["spy_value"].iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Money put in", f"${put_in:,.2f}")
col2.metric("My portfolio", f"${my_value:,.2f}", f"{(my_value / put_in - 1) * 100:+.2f}%")
col3.metric("If all in S&P 500", f"${spy_value:,.2f}", f"{(spy_value / put_in - 1) * 100:+.2f}%")

if my_value > spy_value:
    st.success(f"You're beating the S&P 500 by ${my_value - spy_value:,.2f}")
else:
    st.error(f"You're behind the S&P 500 by ${spy_value - my_value:,.2f}")

st.subheader("You vs. the S&P 500")
fig = go.Figure()
fig.add_scatter(x=spy.index, y=spy["spy_value"], name="If all in S&P 500")
fig.add_scatter(x=spy.index, y=spy["put_in"], name="Money put in", line_shape="hv", line_dash="dot")
fig.add_scatter(x=my_history.index, y=my_history, name="My portfolio")
fig.update_layout(yaxis_tickprefix="$", hovermode="x unified")
st.plotly_chart(fig)

stocks = df[~df["is_cash"]].groupby("symbol")["value"].sum().sort_values(ascending=False)
cash = df.loc[df["is_cash"], "value"].sum()

slices = stocks.head(5).to_dict()
if len(stocks) > 5:
    slices["Everything else"] = stocks.iloc[5:].sum()
if cash > 0:
    slices["Cash"] = cash

left, right = st.columns([1, 2])

with left:
    st.subheader("Top holdings")
    fig = px.pie(names=list(slices.keys()), values=list(slices.values()), hole=0.5)
    st.plotly_chart(fig)

with right:
    st.subheader("Holdings")
    table = df[["symbol", "description", "quantity", "price", "value", "gain", "gain_pct"]]
    st.dataframe(table.round(2), hide_index=True)
