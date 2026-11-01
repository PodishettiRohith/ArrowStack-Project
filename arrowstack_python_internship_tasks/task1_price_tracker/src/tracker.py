import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from src.logger import setup_logger

logger = setup_logger("PriceTracker")

class PriceTrackerLog:
    def __init__(self, csv_path: Path, threshold: float):
        self.csv_path = Path(csv_path)
        self.threshold = threshold
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

    def log_price(self, product_data: dict) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "timestamp": now,
            "title": product_data["title"],
            "price": product_data["price"],
            "availability": product_data["availability"]
        }
        df_new = pd.DataFrame([record])
        if self.csv_path.exists():
            df_new.to_csv(self.csv_path, mode='a', header=False, index=False)
        else:
            df_new.to_csv(self.csv_path, index=False)

        logger.info(f"Price recorded to {self.csv_path}")
        is_below_threshold = product_data["price"] <= self.threshold
        if is_below_threshold:
            logger.warning(f"🚨 PRICE ALERT! Current price {product_data['price']} is at or below target threshold {self.threshold}!")
        return is_below_threshold
