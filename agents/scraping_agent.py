import requests
from bs4 import BeautifulSoup
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_earnings_news():
    """
    Scrapes top 5 earnings reports from Yahoo Finance earnings calendar.
    Returns structured data or a string error message.
    """
    url = "https://finance.yahoo.com/calendar/earnings"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.error(f"❌ HTTP {response.status_code} while fetching data.")
            return "Could not fetch earnings data."

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("table tbody tr")

        highlights = []
        for row in rows[:5]:  # Only top 5 entries
            cols = row.find_all("td")
            if len(cols) >= 6:
                try:
                    company = cols[1].get_text(strip=True)
                    eps_est = cols[4].get_text(strip=True).replace(",", "")
                    eps_act = cols[5].get_text(strip=True).replace(",", "")

                    est = float(eps_est)
                    act = float(eps_act)
                    delta = round(((act - est) / est) * 100, 2)
                    status = "beat" if delta > 0 else "missed"

                    highlights.append({
                        "company": company,
                        "estimate": est,
                        "actual": act,
                        "delta_percent": delta,
                        "status": status
                    })
                except ValueError as ve:
                    logger.warning(f"⚠️ Skipping row due to conversion error: {ve}")
                except Exception as e:
                    logger.error(f"❌ Unexpected error parsing row: {e}")
            else:
                logger.debug("Row skipped due to insufficient columns.")

        return highlights if highlights else "No significant earnings surprises."

    except requests.RequestException as re:
        logger.error(f"Network error: {re}")
        return "Failed to retrieve earnings data due to network issue."
    except Exception as e:
        logger.error(f"Unexpected error during scraping: {e}")
        return f"Earnings scraping failed: {e}"

# Example usage
if __name__ == "__main__":
    earnings_data = scrape_earnings_news()
    if isinstance(earnings_data, list):
        for item in earnings_data:
            print(f"{item['company']} {item['status']} estimates by {item['delta_percent']}%")
    else:
        print(f"ℹ️ {earnings_data}")
