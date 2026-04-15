"""Harness retirado: no git force, bypass de secret scanning ni payouts desde el repo."""

from __future__ import annotations


def tron_precursor_status() -> dict[str, str]:
    """Solo metadatos; sin efectos secundarios."""
    return {
        "module": "tests.tron_precursor",
        "status": "disabled_harness",
        "note": "Tesorería y despliegue: procedimientos manuales validados.",
    }


if __name__ == "__main__":
    print(tron_precursor_status())
