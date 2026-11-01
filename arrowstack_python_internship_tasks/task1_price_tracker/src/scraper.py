import requests
from bs4 import BeautifulSoup
from typing import Dict
from src.logger import setup_logger

logger = setup_logger("WebScraper")

class PriceScraper:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_product_details(self) -> Dict[str, any]:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching URL {self.url}: {e}")
            raise

        soup = BeautifulSoup(response.text, 'html.parser')
        title_elem = soup.select_one("h1") or soup.select_one(".product_main h1")
        price_elem = soup.select_one(".price_color") or soup.select_one(".price")
        stock_elem = soup.select_one(".instock.availability")

        title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
        raw_price = price_elem.get_text(strip=True) if price_elem else "0"
        clean_price_str = ''.join([c for c in raw_price if c.isdigit() or c == '.'])
        price = float(clean_price_str) if clean_price_str else 0.0
        availability = stock_elem.get_text(strip=True) if stock_elem else "Available"

        logger.info(f"Successfully scraped: '{title}' | Price: {price} | Status: {availability}")
        return {"title": title, "price": price, "availability": availability}
