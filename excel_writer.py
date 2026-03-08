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
        self.sheet_name = os.environ.get("EXCEL_SHEET_NAME", "Diete")
        self.user_id    = os.environ.get("ONEDRIVE_USER_ID", "me")
        self.headers    = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

    def _base_url(self) -> str:
        return f"{self.GRAPH_URL}/users/{self.user_id}/drive/root:{self.file_path}"

    def _write_cell(self, cell: str, value):
        url = (
            f"{self._base_url()}:/workbook/worksheets/{self.sheet_name}"
            f"/range(address='{cell}')"
        )
        payload = {"values": [[value]]}
        resp = requests.patch(url, headers=self.headers, json=payload, timeout=15)
        resp.raise_for_status()
        print(f"OK {cell} = {value}")

    def update_or_append(self, nutrition: dict) -> str:
        self._write_cell("D12", nutrition["calories"])
        self._write_cell("C12", nutrition["proteines"])
        self._write_cell("I12", nutrition["glucides"])
        self._write_cell("H12", nutrition["lipides"])
        self._write_cell("L12", nutrition["fibres"])
        return "updated"
