import json
import datetime


def update():
    days = (datetime.date.today() - datetime.date(2026, 4, 1)).days
    total = 16200.0 + (max(0, days) * 1000.0)
    with open("billing_report.json", "w") as f:
        json.dump(
            {"invoice": "F-2026-001", "total_ttc": total, "status": "OVERDUE"},
            f,
            indent=4,
        )
    print(f"📈 DEUDA ACTUALIZADA: {total}€ TTC")


if __name__ == "__main__":
    update()
