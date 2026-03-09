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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "Referer": "https://www.myfitnesspal.com/food/diary",
        })
        cookies_json = os.environ.get("MFP_COOKIES", "{}")
        cookies = json.loads(cookies_json)
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain=".myfitnesspal.com")

    def get_daily_totals(self, target_date: Optional[date] = None) -> dict:
        if target_date is None:
            target_date = date.today()
        date_str = target_date.strftime("%Y-%m-%d")

        url = f"{self.BASE_URL}/api/v2/nutritional-summary"
        params = {"date": date_str}

        resp = self.session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        raw = resp.json()

        return {
            "date": date_str,
            "calories":  raw.get("calories", 0),
            "proteines": raw.get("protein", 0),
            "glucides":  raw.get("carbohydrates", 0),
            "lipides":   raw.get("fat", 0),
            "fibres":    raw.get("fiber", 0),
            "sucres":    raw.get("sugar", 0),
            "sodium":    raw.get("sodium", 0),
        }
