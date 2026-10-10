import csv
import random
from datetime import date, timedelta

from app.config import settings

random.seed(42)
prices = {"Laptop": 55000, "Phone": 22000, "Headphones": 3000, "Tablet": 30000, "Monitor": 12000}
regions = ["North", "South", "East", "West"]

rows = []
for _ in range(300):
    d = date(2025, 1, 1) + timedelta(days=random.randint(0, 364))
    product = random.choice(list(prices))
    region = random.choice(regions)
    units = random.randint(1, 10)
    rows.append([d.isoformat(), d.strftime("%Y-%m"), product, region, units,
                 prices[product], units * prices[product]])

settings.upload_dir.mkdir(parents=True, exist_ok=True)
path = settings.upload_dir / "sales.csv"
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "month", "product", "region", "units", "unit_price", "revenue"])
    writer.writerows(rows)

print(f"Created {path} with {len(rows)} rows")