"""Marca de agua TryOnYou legible — ver docstring largo en repo README o --help."""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PATENTE = "PCT/EP2025/067317"
DEFAULT_LINE = f"© 2026 TryOnYou — {PATENTE} — PAU LE PAON — Confidencial"


def _font(px: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size=px)
            except OSError:
                pass
    return ImageFont.load_default()


def _measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def aplicar_blindaje_pau(
    input_image_path: str | Path,
    output_image_path: str | Path,
    *,
    line1: str | None = None,
    line2: str | None = None,
    band_ratio: float = 0.14,
) -> bool:
    line1 = line1 or os.environ.get("E50_WATERMARK_LINE1", DEFAULT_LINE)
    line2 = line2 or os.environ.get("E50_WATERMARK_LINE2", "").strip()
    try:
        base = Image.open(input_image_path).convert("RGBA")
        w, h = base.size
        main_px = max(22, int(h * 0.024))
        sub_px = max(16, int(h * 0.017))
        font_main = _font(main_px)
        font_sub = _font(sub_px)

        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        band_h = max(int(h * band_ratio), main_px * 3)
        y0 = h - band_h
        draw.rectangle((0, y0, w, h), fill=(0, 0, 0, 200))

        lines = [line1] + ([line2] if line2 else [])
        y = y0 + 14
        for i, text in enumerate(lines):
            font = font_main if i == 0 else font_sub
            tw, th = _measure(draw, text, font)
            x = max(16, (w - tw) // 2)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            y += th + 12

        out = Image.alpha_composite(base, overlay)
        dest = Path(output_image_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        out.convert("RGB").save(dest, "JPEG", quality=92, optimize=True)
        print(f"[+] Blindaje listo: {dest}")
        return True
    except Exception as e:
        print(f"[-] Error: {e}")
        return False


def registrar_distribucion_simulada(image_path: str, entidades: list[str]) -> None:
    print("\n[!] Difusión simulada (sin envío real):")
    time.sleep(0.2)
    for ent in entidades:
        print(f"    · {image_path} → {ent}")
        time.sleep(0.15)
    print("[+] Fin simulación.\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", nargs="?")
    ap.add_argument("salida", nargs="?")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    socios = [
        "Galeries Lafayette (Haussmann)",
        "Bpifrance — inversores",
        "Balmain — lista de espera",
    ]
    if args.demo or not args.entrada:
        print("Demo sin imagen. Uso: python3 protocolo_blindaje_pau_safe.py captura.png salida.jpg")
        registrar_distribucion_simulada("ejemplo_SECURE.jpg", socios)
        return 0
    if not args.salida:
        print("Falta salida.")
        return 1
    if aplicar_blindaje_pau(args.entrada, args.salida):
        registrar_distribucion_simulada(str(args.salida), socios)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
