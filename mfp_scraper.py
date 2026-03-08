import os
import json
import requests
from datetime import date
from typing import Optional


class MFPReportScraper:
    BASE_URL = "https://www.myfitnesspal.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        })
        cookies_json = os.environ.get("MFP_COOKIES", "{}")
        cookies = json.loads(cookies_json)
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain=".myfitnesspal.com")

    def get_daily_totals(self, target_date: Optional[date] = None) -> dict:
        if target_date is None:
            target_date = date.today()
        date_str = target_date.strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/api/v2/diary/{date_str}"
        params = {"fields[]": ["nutritional_contents", "calories", "food_name"]}
        resp = self.session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return self._extract_totals(data, date_str)

    def _extract_totals(self, raw_data: dict, date_str: str) -> dict:
        totals = {
            "date": date_str,
            "calories": 0.0,
            "proteines": 0.0,
            "glucides": 0.0,
            "lipides": 0.0,
            "fibres": 0.0,
            "sucres": 0.0,
            "sodium": 0.0,
        }
        items = raw_data.get("items", [])
        for item in items:
            nc = item.get("nutritional_contents", {})
            totals["calories"]  += nc.get("energy", {}).get("value", 0) or 0
            totals["proteines"] += nc.get("protein", 0) or 0
            totals["glucides"]  += nc.get("carbohydrates", 0) or 0
            totals["lipides"]   += nc.get("fat", 0) or 0
            totals["fibres"]    += nc.get("fiber", 0) or 0
            totals["sucres"]    += nc.get("sugar", 0) or 0
            totals["sodium"]    += nc.get("sodium", 0) or 0
        for key in totals:
            if key != "date":
                totals[key] = round(totals[key], 1)
        return totals
