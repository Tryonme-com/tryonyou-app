"""
Ejecución comercial TryOnYou — Auditoría de Fit (250,00 €).

Genera borradores listos para copiar/pegar o adjuntar en el cliente de correo.
No envía emails (cumplimiento y control humano en el botón «Enviar»).

Marca: TryOnYou (Trae y Yo). Patente: PCT/EP2025/067317 · precisión 0,08 mm.

  python3 TryOnYou_Execution.py

Salida: directorio auditoria_fit_borradores/ (TXT por destinatario).

Bajo Protocolo de Soberanía V10 - Founder: Rubén
Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
"""
from __future__ import annotations

from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "auditoria_fit_borradores"

# Contactos: emails o canales públicos citados en sitios / bases habituales (verificar antes de envío masivo).
CONTACTOS = [
    {
        "marca": "Hermès",
        "zona": "24 rue du Faubourg Saint-Honoré, 75008 Paris",
        "email": "contact@hermes.com",
    },
    {
        "marca": "Chanel",
        "zona": "31 rue Cambon, 75001 Paris",
        "email": "presse.chanel.mode@chanel.com",
    },
    {
        "marca": "AMI Paris",
        "zona": "Rayon 1er / Saint-Honoré — siège 54 rue Étienne Marcel, 75002",
        "email": "info@amiparis.fr",
    },
    {
        "marca": "Jacquemus",
        "zona": "Maison — 69 rue de Monceau, 75008 (cible luxe Paris centre)",
        "email": "customercare@jacquemus.com",
    },
    {
        "marca": "Christian Louboutin",
        "zona": "Flagship Paris / ligne Europe",
        "email": "customerservice-europe@christianlouboutin.fr",
    },
    {
        "marca": "Balmain",
        "zona": "Siège 44 rue François-Ier, 75008",
        "email": "accueil25@balmain.fr",
    },
    {
        "marca": "Celine",
        "zona": "Réseau retail Paris — ligne client EU",
        "email": "clientservice.eu@celine.com",
    },
    {
        "marca": "Saint Laurent (YSL)",
        "zona": "7 avenue George V, 75008",
        "email": "clientservice.fr@ysl.com",
    },
    {
        "marca": "LVMH / Maison Dior (pôle presse groupe)",
        "zona": "Écosystème avenue Montaigne / Saint-Honoré",
        "email": "press@lvmh.com",
    },
    {
        "marca": "Givenchy",
        "zona": "Réseau Paris luxe",
        "email": "clientservice@givenchy.com",
    },
]

COBRO_URL = "https://hook.eu2.make.com/9tlg80gj8sionvb191g40d7we9bj3ovn"
PRECIO = "250,00 €"
MARCA_TYY = "TryOnYou (Trae y Yo)"
PATENTE = "PCT/EP2025/067317"


def cuerpo_correo(nombre_marca: str) -> str:
    return f"""Objet: Proposition — Auditoría de Fit digital · {PRECIO} ({MARCA_TYY})

Madame, Monsieur,

{nombre_marca} impose l’excellence du geste en boutique. {MARCA_TYY} propose une **Auditoría de Fit** ponctuelle : lecture objective du rendu silhouette / essayage numérique, fondée sur notre technologie brevetée **{PATENTE}** (précision **0,08 mm**), pour sécuriser l’expérience client haute exigence.

**Tarif unique de la mission : {PRECIO} TTC** (réservation et déclenchement du flux via le lien ci-dessous).

Lien de engagement / cobro (workflow sécurisé Make) :
{COBRO_URL}

Nous restons à votre disposition pour calibrer le périmètre (flagship, capsule, ou ligne spécifique) sous 48h ouvrées.

Cordialement,
TryOnYou — Espejo Digital Soberano
"""


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for i, row in enumerate(CONTACTOS, start=1):
        slug = f"{i:02d}_{row['marca'].lower().replace(' ', '_').replace('/', '-')}"
        path = OUTPUT_DIR / f"{slug}.txt"
        body = cuerpo_correo(row["marca"])
        content = (
            f"Para: {row['email']}\n"
            f"Marca: {row['marca']}\n"
            f"Ubicación referencia: {row['zona']}\n"
            f"---\n\n"
            f"{body}"
        )
        path.write_text(content, encoding="utf-8")
        print(f"✅ Borrador → {path.relative_to(Path.cwd())}")

    print(f"\nDirectorio: {OUTPUT_DIR}")
    print("Los borradores incluyen el enlace de cobro Make. Pulsa «Enviar» solo tras revisión legal/commercial.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
