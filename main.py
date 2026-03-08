import os
import json
from datetime import date
from mfp_scraper import MFPReportScraper
from excel_writer import ExcelWriter


def main():
    print("🚀 Synchronisation MFP → Excel")

    # Récupérer les données MFP
    scraper = MFPReportScraper()
    nutrition = scraper.get_daily_totals(date.today())
    print(f"📊 Données récupérées : {nutrition}")

    # Écrire dans Excel
    writer = ExcelWriter()
    result = writer.update_or_append(nutrition)
    print(f"✅ Excel mis à jour ({result}) pour le {nutrition['date']}")


if __name__ == "__main__":
    main()
