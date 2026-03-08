import os
import requests


def get_access_token() -> str:
    tenant_id     = os.environ["AZURE_TENANT_ID"]
    client_id     = os.environ["AZURE_CLIENT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
        "scope":         "https://graph.microsoft.com/.default",
    }
    resp = requests.post(url, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()["access_token"]


class ExcelWriter:
    GRAPH_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        self.token      = get_access_token()
        self.file_path  = os.environ["EXCEL_FILE_PATH"]
        self.sheet_name = os.environ.get("EXCEL_SHEET_NAME", "Nutrition")
        self.user_id    = os.environ.get("ONEDRIVE_USER_ID", "me")
        self.headers    = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

    def _base_url(self) -> str:
        return f"{self.GRAPH_URL}/users/{self.user_id}/drive/root:{self.file_path}"

    def _get_next_row(self) -> int:
        url = f"{self._base_url()}:/workbook/worksheets/{self.sheet_name}/usedRange"
        resp = requests.get(url, headers=self.headers, timeout=15)
        resp.raise_for_status()
        return resp.json().get("rowCount", 1) + 1

    def _check_duplicate(self, date_str: str):
        url = f"{self._base_url()}:/workbook/worksheets/{self.sheet_name}/usedRange"
        resp = requests.get(url, headers=self.headers, timeout=15)
        resp.raise_for_status()
        values = resp.json().get("values", [])
        for i, row in enumerate(values[1:], start=2):
            if row and str(row[0]) == date_str:
                return i
        return None

    def update_or_append(self, nutrition: dict) -> str:
        date_str = nutrition["date"]
        row_values = [[
            nutrition["date"],
            nutrition["calories"],
            nutrition["proteines"],
            nutrition["glucides"],
            nutrition["lipides"],
            nutrition["fibres"],
            nutrition["sucres"],
            nutrition["sodium"],
        ]]
        existing_row = self._check_duplicate(date_str)
        row = existing_row if existing_row else self._get_next_row()
        range_addr = f"A{row}:H{row}"
        url = (
            f"{self._base_url()}:/workbook/worksheets/{self.sheet_name}"
            f"/range(address='{range_addr}')"
        )
        payload = {"values": row_values}
        requests.patch(url, headers=self.headers, json=payload, timeout=15)
        return "updated" if existing_row else "inserted"
