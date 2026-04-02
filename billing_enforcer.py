import json
import datetime
import os


def _repo_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def update():
    days = (datetime.date.today() - datetime.date(2026, 4, 1)).days
    total = 16200.0 + (max(0, days) * 1000.0)
    root = _repo_root()
    report_path = os.path.join(root, "billing_report.json")
    with open(report_path, "w") as f:
        json.dump(
            {"invoice": "F-2026-001", "total_ttc": total, "status": "OVERDUE"},
            f,
            indent=4,
        )
    print(f"📈 DEUDA ACTUALIZADA: {total}€ TTC → {report_path}")


if __name__ == "__main__":
    update()
