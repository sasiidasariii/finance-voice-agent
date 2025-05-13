import requests
from bs4 import BeautifulSoup

def scrape_yahoo_earnings():
    """
    Scrapes earnings data from Yahoo Finance earnings calendar.
    
    Returns:
        list: A list of earnings surprises for companies (company name, surprise percentage).
        str: A message indicating the status if no earnings surprises are found.
    """
    url = "https://finance.yahoo.com/calendar/earnings"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Send GET request to fetch the page content
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Error: Failed to retrieve earnings data (HTTP {response.status_code})"
        
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table rows containing earnings data
        rows = soup.select("table tbody tr")
        earnings_data = []
        
        for row in rows[:5]:  # Limit to top 5 results (you can adjust this number as needed)
            cols = row.find_all("td")
            if len(cols) >= 6:
                name = cols[1].text.strip()
                eps_est = cols[4].text.strip()
                eps_act = cols[5].text.strip()

                try:
                    # Calculate earnings surprise (percentage difference)
                    est = float(eps_est)
                    act = float(eps_act)
                    delta = round(((act - est) / est) * 100, 2)
                    status = "beat" if delta > 0 else "missed"
                    earnings_data.append(f"{name} {status} estimates by {abs(delta)}%")
                except ValueError:
                    # Handle any rows with invalid EPS data (skip or log the error)
                    continue
        
        if earnings_data:
            return ". ".join(earnings_data)
        else:
            return "No significant earnings surprises found."

    except Exception as e:
        return f"Error occurred while scraping earnings: {e}"

# Example usage:
if __name__ == "__main__":
    earnings_news = scrape_yahoo_earnings()
    print(f"Earnings News: {earnings_news}")
