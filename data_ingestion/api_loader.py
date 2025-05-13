import yfinance as yf
import logging

# Set up logging for error handling and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_stock_history(ticker: str, period: str = "5d"):
    """
    Fetches historical stock data for the given ticker and period.
    
    Args:
        ticker (str): The stock ticker (e.g., "TSM" for TSMC).
        period (str): The period for which historical data is fetched (default is "5d").

    Returns:
        dict: A dictionary with date, open, close, high, low, volume, etc.
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period=period)

        if history.empty:
            logger.warning(f"No data returned for ticker {ticker} over period {period}.")
            return {"error": f"No data found for {ticker}."}

        # Optionally, filter or process the data before returning
        history_data = history.reset_index().to_dict(orient="records")

        logger.info(f"Fetched {len(history_data)} records for {ticker}.")
        return history_data

    except Exception as e:
        logger.error(f"Error fetching data for ticker {ticker}: {e}")
        return {"error": f"Error fetching data for {ticker}: {str(e)}"}

# Example usage:
if __name__ == "__main__":
    ticker = "TSM"  # Example ticker for TSMC
    stock_data = get_stock_history(ticker)
    if "error" in stock_data:
        print(f"Error: {stock_data['error']}")
    else:
        print(f"Stock Data for {ticker}: {stock_data}")
