#!/usr/bin/env python3
"""
Orquestador Hito 2 (Stripe + sello Antracita + despliegue one-click).

Modo seguro de prueba:
  python3 orquestador_hito2_stripe_antracita.py --dry-run

Modo validacion + despliegue:
  python3 orquestador_hito2_stripe_antracita.py --deploy
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PATENT = "PCT/EP2025/067317"
PROJECT_ROOT = Path(__file__).resolve().parent
TRACE_DIR = PROJECT_ROOT / "logs" / "hito2"
SUMMARY_PATH = TRACE_DIR / "hito2_last_run.json"
SEAL_PATH = TRACE_DIR / "antracita_seal_latest.json"

LIVE_PATTERNS = {
    "stripe_secret": re.compile(r"^sk_live_[A-Za-z0-9_]+$"),
    "stripe_publishable": re.compile(r"^pk_live_[A-Za-z0-9_]+$"),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_id() -> str:
    return f"h2-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"


def _run_capture(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    text = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode, text


def _git_context() -> dict[str, str]:
    branch_rc, branch = _run_capture(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit_rc, commit = _run_capture(["git", "rev-parse", "HEAD"])
    status_rc, status = _run_capture(["git", "status", "--short"])
    return {
        "branch": branch if branch_rc == 0 else "unknown",
        "commit": commit if commit_rc == 0 else "unknown",
        "dirty": "true" if status_rc == 0 and bool(status.strip()) else "false",
    }


def _first_env(*keys: str) -> tuple[str, str]:
    for key in keys:
        value = os.environ.get(key, "").strip()
        if value:
            return key, value
    return "", ""


def _redact(text: str) -> str:
    if not text:
        return text
    cleaned = text
    for rx in (
        re.compile(r"sk_(?:live|test)_[A-Za-z0-9_]+"),
        re.compile(r"pk_(?:live|test)_[A-Za-z0-9_]+"),
        re.compile(r"rk_(?:live|test)_[A-Za-z0-9_]+"),
    ):
        cleaned = rx.sub("[REDACTED]", cleaned)
    token = os.environ.get("VERCEL_TOKEN", "").strip()
    if token:
        cleaned = cleaned.replace(token, "[REDACTED]")
    return cleaned


def _excerpt(text: str, limit: int = 2000) -> str:
    short = _redact(text.strip())
    if len(short) <= limit:
        return short
    return short[:limit] + "...[truncated]"


@dataclass
class StepResult:
    name: str
    required: bool
    status: str
    return_code: int | None
    started_at: str
    finished_at: str
    duration_s: float
    command: str | None = None
    note: str | None = None
    output_excerpt: str | None = None


class TraceWriter:
    def __init__(self, run_id: str) -> None:
        TRACE_DIR.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.path = TRACE_DIR / f"hito2_trace_{run_id}.jsonl"

    def write(self, kind: str, payload: dict[str, Any]) -> None:
        row = {"ts_utc": _utc_now(), "run_id": self.run_id, "kind": kind, **payload}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")


def _validate_environment(mode: str, trace: TraceWriter) -> dict[str, Any]:
    stripe_secret_key, stripe_secret = _first_env(
        "STRIPE_SECRET_KEY_FR",
        "STRIPE_SECRET_KEY_NUEVA",
        "STRIPE_SECRET_KEY",
    )
    stripe_publishable_key, stripe_publishable = _first_env(
        "VITE_STRIPE_PUBLIC_KEY_FR",
        "VITE_STRIPE_PUBLIC_KEY",
    )
    firebase_key, firebase_value = _first_env("VITE_FIREBASE_API_KEY")
    vercel_key, vercel_token = _first_env("VERCEL_TOKEN")

    checks = {
        "stripe_secret": {
            "env": stripe_secret_key or "missing",
            "ok": bool(stripe_secret and LIVE_PATTERNS["stripe_secret"].match(stripe_secret)),
            "expected": "sk_live_*",
        },
        "stripe_publishable": {
            "env": stripe_publishable_key or "missing",
            "ok": bool(
                stripe_publishable
                and LIVE_PATTERNS["stripe_publishable"].match(stripe_publishable)
            ),
            "expected": "pk_live_*",
        },
        "firebase_api_key": {
            "env": firebase_key or "missing",
            "ok": bool(firebase_value),
            "expected": "present",
        },
        "vercel_token": {
            "env": vercel_key or "missing",
            "ok": bool(vercel_token) if mode == "deploy" else True,
            "expected": "present (deploy mode)",
        },
    }

    trace.write("env_validation", {"mode": mode, "checks": checks})
    failed = [name for name, data in checks.items() if not data["ok"]]
    if failed:
        raise RuntimeError(
            "Validacion de entorno fallida: " + ", ".join(failed) + "."
        )
    return checks


def _run_step(
    trace: TraceWriter,
    name: str,
    cmd: list[str] | None = None,
    *,
    required: bool = True,
    note: str | None = None,
    env_overrides: dict[str, str] | None = None,
) -> StepResult:
    started = _utc_now()
    t0 = time.perf_counter()
    if cmd is None:
        finished = _utc_now()
        out = StepResult(
            name=name,
            required=required,
            status="ok",
            return_code=None,
            started_at=started,
            finished_at=finished,
            duration_s=round(time.perf_counter() - t0, 3),
            note=note,
        )
        trace.write("step", out.__dict__)
        return out

    run_env = os.environ.copy()
    if env_overrides:
        run_env.update(env_overrides)

    proc = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        env=run_env,
        capture_output=True,
        text=True,
        check=False,
    )
    finished = _utc_now()
    status = "ok" if proc.returncode == 0 else "failed"
    result = StepResult(
        name=name,
        required=required,
        status=status,
        return_code=proc.returncode,
        started_at=started,
        finished_at=finished,
        duration_s=round(time.perf_counter() - t0, 3),
        command=" ".join(cmd),
        note=note,
        output_excerpt=_excerpt((proc.stdout or "") + (proc.stderr or "")),
    )
    trace.write("step", result.__dict__)
    if required and proc.returncode != 0:
        raise RuntimeError(f"Fallo en paso requerido: {name}")
    return result


def _write_antracita_seal(
    mode: str,
    run_id: str,
    trace: TraceWriter,
    git_ctx: dict[str, str],
    env_checks: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "seal": "ANTRACITA",
        "hito": 2,
        "status": "READY_FOR_ONE_CLICK_DEPLOY",
        "mode": mode,
        "run_id": run_id,
        "ts_utc": _utc_now(),
        "patent": PATENT,
        "one_click_command": "./boton_bunker_hito2.sh",
        "dry_run_command": "python3 orquestador_hito2_stripe_antracita.py --dry-run",
        "trace_file": str(trace.path.relative_to(PROJECT_ROOT)),
        "summary_file": str(SUMMARY_PATH.relative_to(PROJECT_ROOT)),
        "git": git_ctx,
        "env_checks": {
            name: {"env": data["env"], "ok": data["ok"]} for name, data in env_checks.items()
        },
    }
    with SEAL_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
        f.write("\n")
    trace.write("antracita_seal", {"path": str(SEAL_PATH.relative_to(PROJECT_ROOT))})
    return payload


def _write_summary(
    run_id: str,
    mode: str,
    trace: TraceWriter,
    git_ctx: dict[str, str],
    steps: list[StepResult],
    status: str,
    error: str | None = None,
) -> None:
    summary = {
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "error": error,
        "ts_utc": _utc_now(),
        "patent": PATENT,
        "git": git_ctx,
        "trace_file": str(trace.path.relative_to(PROJECT_ROOT)),
        "steps": [s.__dict__ for s in steps],
    }
    with SUMMARY_PATH.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=True)
        f.write("\n")


def run_pipeline(mode: str) -> int:
    run_id = _run_id()
    trace = TraceWriter(run_id=run_id)
    git_ctx = _git_context()
    steps: list[StepResult] = []
    trace.write("pipeline_start", {"mode": mode, "git": git_ctx})

    try:
        env_checks = _validate_environment(mode=mode, trace=trace)
        _write_antracita_seal(
            mode=mode,
            run_id=run_id,
            trace=trace,
            git_ctx=git_ctx,
            env_checks=env_checks,
        )
        steps.append(_run_step(trace, "validacion_70", ["python3", "validacion_70.py"]))
        steps.append(
            _run_step(
                trace,
                "sellado_bunker_omega",
                ["python3", "sellar_bunker_omega.py"],
                env_overrides={
                    "E50_PROJECT_ROOT": str(PROJECT_ROOT),
                    "E50_WRITE_SEAL": "1",
                },
            )
        )
        steps.append(_run_step(trace, "check_env_vars", ["python3", "check_env_vars.py"]))
        steps.append(_run_step(trace, "stripe_tests", ["python3", "-m", "unittest", "tests/test_stripe_lafayette.py", "tests/test_stripe_agent.py"]))
        steps.append(_run_step(trace, "frontend_build", ["npm", "run", "build"]))

        if mode == "deploy":
            steps.append(
                _run_step(
                    trace,
                    "stripe_secret_live_check",
                    ["python3", "stripe_verify_secret_env.py", "--funding"],
                )
            )
            steps.append(
                _run_step(
                    trace,
                    "vercel_deploy",
                    ["python3", "vercel_deploy_orchestrator.py"],
                    note="Despliegue real a Vercel",
                )
            )
            verify_url = os.environ.get("VERIFY_VERCEL_URL", "").strip()
            if verify_url:
                steps.append(
                    _run_step(
                        trace,
                        "post_deploy_healthcheck",
                        ["python3", "scripts/verify_vercel_health.py", verify_url],
                    )
                )
            else:
                steps.append(
                    _run_step(
                        trace,
                        "post_deploy_healthcheck_skipped",
                        note="Define VERIFY_VERCEL_URL para healthcheck post-deploy.",
                        required=False,
                    )
                )
        else:
            steps.append(
                _run_step(
                    trace,
                    "deploy_skipped_dry_run",
                    note="Modo dry-run: no se ejecutan Stripe API live ni Vercel deploy.",
                    required=False,
                )
            )

        _write_summary(
            run_id=run_id,
            mode=mode,
            trace=trace,
            git_ctx=git_ctx,
            steps=steps,
            status="ok",
        )
        trace.write("pipeline_end", {"status": "ok"})
        print(f"OK Hito 2 ({mode}) | trace={trace.path} | summary={SUMMARY_PATH}")
        return 0
    except Exception as exc:  # noqa: BLE001
        _write_summary(
            run_id=run_id,
            mode=mode,
            trace=trace,
            git_ctx=git_ctx,
            steps=steps,
            status="failed",
            error=str(exc),
        )
        trace.write("pipeline_end", {"status": "failed", "error": str(exc)})
        print(f"ERROR Hito 2 ({mode}): {exc}", file=sys.stderr)
        print(f"Revisa: {trace.path}", file=sys.stderr)
        return 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="One-click validator/deployer para Stripe + sello Antracita (Hito 2)."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecuta validaciones y build sin deploy real.",
    )
    mode.add_argument(
        "--deploy",
        action="store_true",
        help="Ejecuta validaciones y despliegue real.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    mode = "dry-run" if args.dry_run else "deploy"
    return run_pipeline(mode=mode)


if __name__ == "__main__":
    raise SystemExit(main())
