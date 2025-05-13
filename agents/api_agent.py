import yfinance as yf
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_market_data():
    """
    Fetch market data for selected tech stocks and calculate exposure.
    Retrieves last 2 days of closing prices and computes allocation exposure.
    """
    tickers = ["TSM", "AAPL"]  # More reliable tickers than SSNLF
    data = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            
            # Ensure 2 days of data
            if len(hist) < 2:
                logger.warning(f"Insufficient data for {ticker}: Only {len(hist)} day(s) found.")
                return None

            data[ticker] = hist["Close"].tolist()
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    asia_tech_today = calculate_exposure(data, date="today")
    asia_tech_yesterday = calculate_exposure(data, date="yesterday")

    return {
        "asia_tech_today": asia_tech_today,
        "asia_tech_yesterday": asia_tech_yesterday
    }

def calculate_exposure(data, date):
    """
    Sum up the closing prices for the tickers for the specified day.
    """
    exposure = 0
    for ticker in data:
        try:
            if date == "today":
                exposure += data[ticker][1]
            elif date == "yesterday":
                exposure += data[ticker][0]
        except IndexError:
            logger.error(f"Missing or insufficient data for {ticker} on {date}. Prices: {data[ticker]}")
            return None
    return exposure

# Example test usage
if __name__ == "__main__":
    market_data = fetch_market_data()
    if market_data:
        logger.info(f"✅ Market Data: {market_data}")
    else:
        logger.error("❌ Failed to fetch complete market data.")
