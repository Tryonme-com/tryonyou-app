import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SupercommitMaxTest(unittest.TestCase):
    def test_bash_syntax(self):
        for name in ("supercommit_max.sh", "Supercommit_Max"):
            script = ROOT / name
            self.assertTrue(script.is_file(), name)
            completed = subprocess.run(
                ["bash", "-n", str(script)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_script_rejects_force_push_and_hardcoded_bot_token(self):
        text = (ROOT / "supercommit_max.sh").read_text(encoding="utf-8")
        self.assertNotIn("push --force", text)
        self.assertNotIn("push -f", text)
        self.assertIn("https://api.telegram.org/bot${token}/sendMessage", text)
        self.assertIn("TRYONYOU_DEPLOY_BOT_TOKEN", text)
        self.assertIn('branch" == "main"', text)
        self.assertNotRegex(text, r"\d{6,}:[A-Za-z0-9_-]{10,}")

    def test_env_example_has_empty_secret_slots(self):
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertNotIn("Basándome en los documentos", text)
        self.assertNotIn("```", text)
        required_empty = {
            "VERCEL_TOKEN",
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "TRYONYOU_DEPLOY_BOT_TOKEN",
            "TRYONYOU_DEPLOY_CHAT_ID",
            "PORKBUN_API_KEY",
            "VERCEL_ORG_ID",
            "VERCEL_PROJECT_ID",
            "TRYONYOU_CAPITAL_450K_CONFIRMED",
        }
        seen = {}
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, raw = stripped.partition("=")
            value = raw.split("#", 1)[0].strip().strip('"').strip("'")
            seen[key.strip()] = value
        for key in required_empty:
            self.assertIn(key, seen)
            self.assertEqual(seen[key], "", key)

    def test_gallery_keeps_vite_shell_and_oberkampf_node(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="root"', index)
        self.assertIn('/src/main.tsx', index)
        app = (ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
        live = (ROOT / "src" / "App.jsx").read_text(encoding="utf-8")
        self.assertIn('"75011"', app)
        self.assertIn("Búnker Oberkampf 75011", live)
        self.assertIn("BUNKER_OBERKAMPF", live)
        self.assertIn('id="bunker-postal-node"', live)
        self.assertIn('import App from "./App.jsx"', (ROOT / "src" / "main.tsx").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
