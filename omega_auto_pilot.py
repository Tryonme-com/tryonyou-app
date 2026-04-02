import requests
import json
import datetime
import subprocess


def main():
    print(f"=== OMEGA AUTO-PILOT ACTIVADO [{datetime.datetime.now()}] ===")
    try:
        res = requests.post(
            "https://hook.eu2.make.com/9tlg80gj8sionvb191g40d7we9bj3ovn",
            json={"status": "trigger_50_agents"},
            timeout=120,
        )
        print(f"📡 MAKE.COM: Status {res.status_code}")
    except Exception:
        print("❌ MAKE.COM: Fallo")
    with open("node_lock_status.json", "w") as f:
        json.dump(
            {"node": "75009", "restriction": "LOCKED", "debt": 16200.0},
            f,
            indent=4,
        )
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", "🚨 OMEGA: Auto-Pilot Execution"],
            check=True,
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
