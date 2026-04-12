"""
BUNKER_AUTO_PILOT
-----------------
Monitor autonomo de PRs financieros para TryOnYou:

1) Detecta PRs abiertas con foco "Bancaria"/"Settlement" (#187/#182).
2) Valida estado Render y salud de Stripe webhooks.
3) Ejecuta Supercommit_Max para sincronizacion operativa.
4) Fusiona PR automaticamente si todo pasa.
5) Reporta exitos por Telegram (bot deploy).
6) El martes a las 08:00 (Europa/Paris), confirma capital y activa Dossier Fatality.

Nunca hardcodea secretos. Usa variables de entorno.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

PATENT = "PCT/EP2025/067317"
SOVEREIGN_PROTOCOL = "Bajo Protocolo de Soberania V10 - Founder: Ruben"
DEFAULT_FINANCIAL_IMPACT_EUR = 51988.50
DEFAULT_CAPITAL_ENTRY_EUR = 450000.00


@dataclass(frozen=True)
class PilotConfig:
    github_repo: str
    github_token: str
    telegram_token: str
    telegram_chat_id: str
    render_health_url: str
    stripe_webhook_health_url: str
    financial_impact_eur: float
    capital_entry_target_eur: float
    capital_entry_confirmed: bool
    timezone_name: str


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "")
    if not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "si"}


def _load_config() -> PilotConfig:
    token = (
        os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_TOKEN", "").strip()
    )
    return PilotConfig(
        github_repo=os.getenv("BUNKER_GITHUB_REPO", "tryonme-com/tryonyou-app").strip(),
        github_token=os.getenv("GITHUB_TOKEN", "").strip(),
        telegram_token=token,
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "@tryonyou_deploy_bot").strip(),
        render_health_url=os.getenv("RENDER_HEALTHCHECK_URL", "").strip(),
        stripe_webhook_health_url=os.getenv("STRIPE_WEBHOOK_HEALTH_URL", "").strip(),
        financial_impact_eur=float(
            os.getenv("BUNKER_FINANCIAL_IMPACT_EUR", str(DEFAULT_FINANCIAL_IMPACT_EUR))
        ),
        capital_entry_target_eur=float(
            os.getenv("BUNKER_CAPITAL_ENTRY_EUR", str(DEFAULT_CAPITAL_ENTRY_EUR))
        ),
        capital_entry_confirmed=_env_bool("BUNKER_CAPITAL_ENTRY_CONFIRMED", default=False),
        timezone_name=os.getenv("BUNKER_TIMEZONE", "Europe/Paris").strip(),
    )


class AutonomousEmpire:
    def __init__(self, config: PilotConfig | None = None) -> None:
        self.config = config or _load_config()
        self.base_github_api = f"https://api.github.com/repos/{self.config.github_repo}"
        self.repo_root = Path(__file__).resolve().parent

    def _gh_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.config.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _log(self, text: str) -> None:
        print(f"[BUNKER_AUTO_PILOT] {text}")

    def _target_pr(self, pr: dict[str, Any]) -> bool:
        content = f"{pr.get('title', '')}\n{pr.get('body', '')}".lower()
        keywords = ("bancaria", "settlement", "#187", "#182")
        number = pr.get("number")
        if isinstance(number, int) and number in (182, 187):
            return True
        return any(word in content for word in keywords)

    def _list_open_prs(self) -> list[dict[str, Any]]:
        if not self.config.github_token:
            self._log("Sin GITHUB_TOKEN: no se puede listar PRs.")
            return []
        try:
            response = requests.get(
                f"{self.base_github_api}/pulls",
                headers=self._gh_headers(),
                params={"state": "open", "per_page": 100},
                timeout=30,
            )
            if response.status_code != 200:
                self._log(f"GitHub PR list HTTP {response.status_code}: {response.text[:180]}")
                return []
            payload = response.json()
            if isinstance(payload, list):
                return payload
        except requests.RequestException as exc:
            self._log(f"Error consultando PRs: {exc}")
        return []

    def _validate_render(self) -> tuple[bool, str]:
        url = self.config.render_health_url
        if not url:
            return False, "RENDER_HEALTHCHECK_URL no configurado"
        try:
            response = requests.get(url, timeout=30)
            if 200 <= response.status_code < 300:
                return True, f"Render OK ({response.status_code})"
            return False, f"Render no saludable (HTTP {response.status_code})"
        except requests.RequestException as exc:
            return False, f"Render error de red: {exc}"

    def _run_local_stripe_tests(self) -> tuple[bool, str]:
        cmd = [
            sys.executable,
            "-m",
            "unittest",
            "tests.test_stripe_webhook",
            "tests.test_stripe_handler",
        ]
        result = subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True, "Stripe webhook tests OK (suite local)"
        err = (result.stderr or result.stdout or "").strip().replace("\n", " ")
        return False, f"Stripe tests fallidos: {err[:240]}"

    def _validate_stripe_webhooks(self) -> tuple[bool, str]:
        url = self.config.stripe_webhook_health_url
        if url:
            try:
                response = requests.get(url, timeout=30)
                if 200 <= response.status_code < 300:
                    return True, f"Stripe webhook endpoint OK ({response.status_code})"
                return False, f"Stripe webhook endpoint HTTP {response.status_code}"
            except requests.RequestException as exc:
                return False, f"Stripe webhook endpoint error: {exc}"
        return self._run_local_stripe_tests()

    def _run_supercommit_max(self) -> tuple[bool, str]:
        script = self.repo_root / "supercommit_max.sh"
        if not script.is_file():
            return False, "supercommit_max.sh no encontrado"
        cmd = ["bash", str(script), "--fast", "--msg", "Auto-sync bunker galeria web"]
        result = subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            msg = (result.stderr or result.stdout or "").strip().replace("\n", " ")
            return False, f"Supercommit_Max fallo: {msg[:240]}"
        return True, "Supercommit_Max ejecutado"

    def _bash_syntax_check(self) -> tuple[bool, str]:
        scripts = [
            self.repo_root / "supercommit_max.sh",
            self.repo_root / "TRYONYOU_SUPERCOMMIT_MAX.sh",
            self.repo_root / "SUPERCOMMIT.sh",
        ]
        for script in scripts:
            if not script.is_file():
                continue
            result = subprocess.run(
                ["bash", "-n", str(script)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout or "").strip().replace("\n", " ")
                return False, f"Sintaxis Bash invalida en {script.name}: {detail[:180]}"
        return True, "Sintaxis Bash validada (galeria 10/10)"

    def _merge_pr(self, pr_number: int) -> tuple[bool, str]:
        if not self.config.github_token:
            return False, "Sin GITHUB_TOKEN para merge"
        payload = {
            "commit_title": (
                f"Auto-merge PR #{pr_number} | "
                f"@CertezaAbsoluta @lo+erestu {PATENT} {SOVEREIGN_PROTOCOL}"
            )
        }
        try:
            response = requests.put(
                f"{self.base_github_api}/pulls/{pr_number}/merge",
                headers=self._gh_headers(),
                json=payload,
                timeout=30,
            )
            if response.status_code == 200:
                return True, "PR fusionada correctamente"
            return False, f"Merge rechazado HTTP {response.status_code}: {response.text[:180]}"
        except requests.RequestException as exc:
            return False, f"Merge error de red: {exc}"

    def _telegram_report(self, message: str) -> bool:
        if not self.config.telegram_token or not self.config.telegram_chat_id:
            self._log("Telegram no configurado; se omite reporte.")
            return False
        payload = {
            "chat_id": self.config.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        url = f"https://api.telegram.org/bot{self.config.telegram_token}/sendMessage"
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return True
            self._log(f"Telegram HTTP {response.status_code}: {response.text[:200]}")
        except requests.RequestException as exc:
            self._log(f"Telegram error: {exc}")
        return False

    def _is_tuesday_0800(self, now: datetime) -> bool:
        return now.weekday() == 1 and now.hour == 8

    def _activate_dossier_fatality(self, now: datetime) -> tuple[bool, str]:
        if not self.config.capital_entry_confirmed:
            return False, "Capital no confirmado por entorno (BUNKER_CAPITAL_ENTRY_CONFIRMED)"
        artifact = {
            "activated_at": now.isoformat(),
            "capital_entry_eur": self.config.capital_entry_target_eur,
            "status": "DOSSIER_FATALITY_ACTIVE",
            "patent": PATENT,
            "protocol": SOVEREIGN_PROTOCOL,
        }
        output = self.repo_root / "dossier_fatality_activation.json"
        output.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        return True, f"Dossier Fatality activado ({output.name})"

    def _security_routine(self) -> None:
        tz = ZoneInfo(self.config.timezone_name)
        now = datetime.now(tz)
        if not self._is_tuesday_0800(now):
            self._log("Fuera de ventana Martes 08:00; rutina de seguridad en espera.")
            return
        ok, detail = self._activate_dossier_fatality(now)
        if ok:
            self._telegram_report(
                (
                    "✅ *Seguridad TryOnYou*\\n"
                    f"Capital confirmado: `{self.config.capital_entry_target_eur:,.2f} €`\\n"
                    f"{detail}\\n"
                    f"{PATENT}"
                )
            )
            self._log(detail)
            return
        self._log(f"Rutina de seguridad no activada: {detail}")

    def _process_pr(self, pr: dict[str, Any]) -> None:
        number = pr.get("number")
        title = pr.get("title", "")
        if not isinstance(number, int):
            return
        self._log(f"Procesando PR #{number}: {title}")

        checks: list[tuple[str, bool, str]] = []
        render_ok, render_msg = self._validate_render()
        checks.append(("Render", render_ok, render_msg))
        stripe_ok, stripe_msg = self._validate_stripe_webhooks()
        checks.append(("Stripe", stripe_ok, stripe_msg))
        sync_ok, sync_msg = self._run_supercommit_max()
        checks.append(("Supercommit_Max", sync_ok, sync_msg))
        bash_ok, bash_msg = self._bash_syntax_check()
        checks.append(("Bash", bash_ok, bash_msg))

        all_ok = all(item[1] for item in checks)
        for service, ok, detail in checks:
            status = "OK" if ok else "FAIL"
            self._log(f"{service}: {status} - {detail}")

        if not all_ok:
            self._log(f"PR #{number} no fusionada: checks incompletos.")
            return

        merged, merge_msg = self._merge_pr(number)
        self._log(f"Merge PR #{number}: {merge_msg}")
        if not merged:
            return

        self._telegram_report(
            (
                "✅ *Exito de Autopilot TryOnYou*\\n"
                f"PR #{number} fusionada: `{title}`\\n"
                f"Impacto financiero: `{self.config.financial_impact_eur:,.2f} €`\\n"
                f"Estado: Render + Stripe + Supercommit_Max + Bash en verde\\n"
                f"{PATENT}"
            )
        )

    def process_all_requests(self) -> None:
        self._security_routine()
        prs = self._list_open_prs()
        targets = [pr for pr in prs if self._target_pr(pr)]
        if not targets:
            self._log("Sin PRs objetivo (Bancaria/Settlement).")
            return
        self._log(f"PRs objetivo detectadas: {len(targets)}")
        for pr in targets:
            self._process_pr(pr)


def main() -> int:
    pilot = AutonomousEmpire()
    pilot.process_all_requests()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
