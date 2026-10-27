# Portfolio Tracker

Did your investing beat just buying the S&P 500?

Upload a Fidelity positions CSV, paste in your deposits, and the app compares your portfolio against what the same deposits would be worth if you had just bought SPY on the same day.

## Features
- You VS S&P 500 comparison, adjusted for when you added money
- Chart of your portfolio VS the S&P 500 over time
- Top 5 holdings breakdown

## Run it
    pip install -r requirements.txt
    streamlit run app.py

Built with Python, pandas, Streamlit, Plotly, and yfinance.