import pytest
from unittest.mock import patch
from src.scraper import PriceScraper
from src.tracker import PriceTrackerLog

SAMPLE_HTML = """
<html>
    <body>
        <div class="product_main">
            <h1>A Light in the Attic</h1>
            <p class="price_color">£51.77</p>
            <p class="instock availability">In stock</p>
        </div>
    </body>
</html>
"""

class MockResponse:
    text = SAMPLE_HTML
    def raise_for_status(self):
        pass

@patch("requests.get", return_value=MockResponse())
def test_scraper_extraction(mock_get):
    scraper = PriceScraper("https://fake-store.com/item")
    data = scraper.fetch_product_details()
    assert data["title"] == "A Light in the Attic"
    assert data["price"] == 51.77
    assert "In stock" in data["availability"]

def test_tracker_threshold(tmp_path):
    csv_file = tmp_path / "history.csv"
    tracker = PriceTrackerLog(csv_file, threshold=60.00)
    product = {"title": "Test Book", "price": 45.00, "availability": "In stock"}
    alert_triggered = tracker.log_price(product)
    assert alert_triggered is True
    assert csv_file.exists()
