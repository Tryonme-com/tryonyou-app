"""
Equipo 50: npm + stub firebase + git (opcional).

⚠️  No uses subprocess.run([...], shell=True) con lista.
⚠️  git add/commit/push solo con E50_GIT_PUSH=1 (evita subir .env y push accidental).
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))


def _run(argv: list[str]) -> bool:
    try:
        return subprocess.run(argv, cwd=ROOT, check=False).returncode == 0
    except OSError as e:
        print(f"❌ {e}")
        return False


def conectar_equipo_50() -> None:
    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    print("🛠️ Jules: npm install (lock + deps)...")
    if not _run(["npm", "install"]):
        print("❌ npm install falló.")
        sys.exit(1)

    print("🛡️ Agente 70: firebase.ts (fallback demo + variables Vite)...")
    fb_path = os.path.join(ROOT, "src", "lib", "firebase.ts")
    os.makedirs(os.path.dirname(fb_path), exist_ok=True)
    fb_code = """import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY ?? 'AIzaSy_DUMMY',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN ?? 'demo.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID ?? 'demo-project',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET ?? 'demo.appspot.com',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID ?? '0000000000',
  appId: import.meta.env.VITE_FIREBASE_APP_ID ?? '1:000:web:000',
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
export const auth = getAuth(app);
export default app;
"""
    with open(fb_path, "w", encoding="utf-8") as f:
        f.write(fb_code.strip() + "\n")

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return

    print("🧹 Equipo 50: git add (acotado), commit...")
    _run(["git", "add", "src/", "package.json", "package-lock.json", ".gitignore"])
    _run(["git", "commit", "-m", "MESA_LITIS_TOTAL: Conexión equipo 50 y limpieza de build"])

    print("🚀 Push --force main...")
    if _run(["git", "push", "origin", "main", "--force"]):
        print("🔥 Push enviado. Revisa Vercel / GitHub.")
    else:
        print("❌ Push falló (credenciales, rama o remoto).")
        sys.exit(1)


if __name__ == "__main__":
    conectar_equipo_50()
