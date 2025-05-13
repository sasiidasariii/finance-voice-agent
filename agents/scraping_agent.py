# agents/scraping_agent.py
import requests
from bs4 import BeautifulSoup

def get_earnings_summary(url: str):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    earnings = soup.find_all("p")
    return " ".join([p.get_text() for p in earnings[:5]])
