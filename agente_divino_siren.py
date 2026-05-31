"""
Agente de escucha «Divino» — soporte técnico minimalista sobre el SIREN 943 610 196.

Modo interactivo (stdin). Tono: sobrio, Lafayette / ligne claire.

  python3 agente_divino_siren.py

Salir: línea vacía o Ctrl+D.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import re
import sys

SIREN = "943610196"
SIREN_FMT = "943 610 196"


def _divino(respuesta: str) -> None:
    print(f"· {respuesta}\n")


def contestar(texto: str) -> None:
    t = texto.lower().strip()
    if not t:
        return

    if re.search(r"siren|siret|rne|immatricul", t):
        _divino(
            f"Le SIREN {SIREN_FMT} identifie l’unité légale — ancrage républicain, "
            "traçabilité contractuelle. Pour le détail public : service-public.fr / infogreffe."
        )
        return
    if re.search(r"facture|tva|tva intracom|numéro de tva", t):
        _divino(
            "Toute exigence fiscale se règle sur pièces officielles. "
            "Le SIREN suffit aux interlocuteurs institutionnels pour corréler la raison sociale."
        )
        return
    if re.search(r"patente|brevet|pct|067317|0[,.]08|mm|précision", t):
        _divino(
            "La couverture PCT/EP2025/067317 protège le cœur métrique du miroir numérique — "
            "précision annoncée 0,08 mm : c’est la grammaire technique, pas le folklore retail."
        )
        return
    if re.search(r"donnée|rgpd|dpo|privacy", t):
        _divino(
            "Le traitement est minimal et opposable : finalité, base légale, durée. "
            f"SIREN {SIREN_FMT} : point d’ancrage pour vos DPA et mentions."
        )
        return

    _divino(
        f"SIREN {SIREN_FMT} — ligne claire. Précisez : immatriculation, fiscalité, propriété industrielle ou données. "
        "Nous répondons avec la même netteté."
    )


def main() -> int:
    print("Agente Divino · SIREN — écrie. Vacío para salir.\n")
    try:
        while True:
            line = sys.stdin.readline()
            if line == "":
                break
            if line.strip() == "":
                break
            contestar(line)
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
