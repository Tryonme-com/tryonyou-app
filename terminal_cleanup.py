import os
import shutil


def clean():
    for t in ["__pycache__", "temp_deploy"]:
        if os.path.exists(t):
            shutil.rmtree(t)
    if os.path.exists("production_status.json"):
        os.chmod("production_status.json", 0o444)
    print("🧹 LIMPIEZA COMPLETADA")


if __name__ == "__main__":
    clean()
