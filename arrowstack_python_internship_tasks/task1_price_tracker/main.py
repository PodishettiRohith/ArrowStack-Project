import os
from pathlib import Path
from dotenv import load_dotenv
from src.scraper import PriceScraper
from src.tracker import PriceTrackerLog
from src.logger import setup_logger

load_dotenv()
logger = setup_logger("Main")

def main():
    target_url = os.getenv("TARGET_URL", "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
    threshold = float(os.getenv("PRICE_THRESHOLD", "60.00"))
    csv_path = Path("data/price_history.csv")

    logger.info(f"Starting Price Tracker for URL: {target_url}")
    scraper = PriceScraper(target_url)
    tracker = PriceTrackerLog(csv_path, threshold=threshold)

    try:
        product_data = scraper.fetch_product_details()
        tracker.log_price(product_data)
        logger.info("Price check completed successfully!")
    except Exception as e:
        logger.error(f"Price tracking execution failed: {e}")

if __name__ == "__main__":
    main()
