import os
import json
import requests
from datetime import date
from typing import Optional


class MFPReportScraper:

    def __init__(self):
        self.cookies = json.loads(os.environ.get("MFP_COOKIES", "{}"))

    def get_daily_totals(self, target_date: Optional[date] = None) -> dict:
        if target_date is None:
            target_date = date.today()
        date_str = target_date.strftime("%Y-%m-%d")

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "mfp-client-id": "mfp-main-js",
            "mfp-user-id": os.environ.get("MFP_USER_ID", ""),
        })
        for name, value in self.cookies.items():
            session.cookies.set(name, value, domain=".myfitnesspal.com")

        url = f"https://www.myfitnesspal.com/api/v2/diary"
        params = {"date": date_str}
        resp = session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        raw = resp.json()

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
        for item in raw.get("items", []):
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
