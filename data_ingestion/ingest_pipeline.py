from .api_loader import get_stock_history
from .scraping_agent import scrape_earnings_news  # Assuming scraping agent is implemented here
import logging

# Set up logging for error handling
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline(ticker="TSM"):
    """
    Runs the data ingestion pipeline. Fetches stock data and earnings news.

    Args:
        ticker (str): Stock ticker symbol (default is "TSM").

    Returns:
        dict: Contains stock history and earnings news. Returns error messages if any.
    """
    data = {}

    try:
        # Fetch stock history
        logger.info(f"Fetching stock history for {ticker}...")
        stock_history = get_stock_history(ticker)
        if "error" in stock_history:
            logger.error(f"Error fetching stock history: {stock_history['error']}")
        else:
            data["history"] = stock_history

        # Fetch earnings news
        logger.info(f"Fetching earnings news...")
        earnings_news = scrape_earnings_news()
        if earnings_news.startswith("Error") or earnings_news == "":
            logger.error(f"Error fetching earnings news: {earnings_news}")
        else:
            data["news"] = earnings_news

    except Exception as e:
        logger.error(f"Error running the pipeline: {e}")
        data["error"] = f"Error running the pipeline: {str(e)}"

    return data

# Example usage
if __name__ == "__main__":
    ticker = "TSM"  # Example ticker for TSMC
    result = run_pipeline(ticker)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Data for {ticker}: {result}")
