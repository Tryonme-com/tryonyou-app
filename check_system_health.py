import subprocess
import datetime


def check():
    print(f"=== SALUD VERCEL [{datetime.datetime.now()}] ===")
    subprocess.run(["vercel", "logs", "tryonyou-app", "-n", "10"])


if __name__ == "__main__":
    check()
