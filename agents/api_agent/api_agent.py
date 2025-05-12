import yfinance as yf

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    return {
        "ticker": ticker,
        "close": data["Close"].iloc[-1] if not data.empty else None,
        "change": data["Close"].pct_change().iloc[-1] * 100 if len(data) > 1 else None
    }
