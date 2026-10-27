import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from compare import spy_history
from history import add_today
from parse import load_positions
from prices import add_live_values

st.set_page_config(page_title="Portfolio Tracker", layout="wide")
st.title("Portfolio Tracker")

uploaded = st.file_uploader("Upload your Fidelity positions CSV", type="csv")
history_file = st.sidebar.file_uploader("Your history file (optional)", type="csv")

st.sidebar.subheader("Your deposits")
text = st.sidebar.text_area(
    "Paste one deposit per line as date,amount",
    placeholder="2026-06-15,300\n2026-08-24,400",
    height=250,
)

deposits = []
for line in text.strip().splitlines():
    if not line.strip():
        continue
    try:
        date, amount = line.split(",")
        deposits.append((pd.Timestamp(date.strip()), float(amount.strip().replace("$", ""))))
    except ValueError:
        st.sidebar.warning(f"Couldn't read this line: {line}")

if uploaded is None:
    st.info("Upload your Fidelity positions CSV to get started.")
    st.stop()

df = load_positions(uploaded)
df = add_live_values(df)
my_value = df["value"].sum()

my_history = add_today(history_file, my_value)
st.sidebar.download_button(
    "Download updated history",
    my_history.to_csv(index=False),
    file_name="portfolio_history.csv",
)

if not deposits:
    st.metric("My portfolio", f"${my_value:,.2f}")
    st.error("Add your deposits in the sidebar to compare against the S&P 500.")
else:
    put_in = sum(amount for date, amount in deposits)
    history = spy_history(deposits)
    spy_value = history["spy_value"].iloc[-1]

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
    fig.add_scatter(x=history.index, y=history["spy_value"], name="If all in S&P 500")
    fig.add_scatter(x=history.index, y=history["put_in"], name="Money put in", line_shape="hv", line_dash="dot")
    fig.add_scatter(x=my_history["date"], y=my_history["value"], name="My portfolio", mode="lines+markers")
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