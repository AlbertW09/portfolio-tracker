# Portfolio Tracker

Did your investing beat just buying the S&P 500? Let's find out!

Upload your Fidelity positions and activity CSVs, and the app compares your portfolio against what the same deposits would be worth if you had just bought SPY on the same day.

## Features
- You VS S&P 500 comparison, adjusted for when you added money
- Daily history of your portfolio, rebuilt from your trades and historical prices
- Chart of your portfolio VS the S&P 500 over time
- Top 5 holdings breakdown

## Getting your files from Fidelity
- **Positions:** Positions page → Download
- **Activity:** Activity & Orders page → pick a date range that covers your whole account history → Download

## Run it
    pip install -r requirements.txt
    streamlit run app.py

Built with Python, pandas, Streamlit, Plotly, and yfinance.