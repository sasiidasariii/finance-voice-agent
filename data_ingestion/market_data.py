import yfinance as yf

def fetch_historical_prices(ticker: str, period: str = "5d", interval: str = "1d"):
    stock = yf.Ticker(ticker)
    return stock.history(period=period, interval=interval)

def fetch_stock_summary(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "symbol": info.get("symbol"),
        "sector": info.get("sector"),
        "price": info.get("regularMarketPrice"),
        "marketCap": info.get("marketCap"),
        "peRatio": info.get("trailingPE"),
        "eps": info.get("trailingEps")
    }
