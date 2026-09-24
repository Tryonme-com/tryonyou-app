import os
import subprocess
import time

REPORTE_DEFAULT = "REPORTE_ESTRATEGICO_DIVINEO.txt"
INTERVALO_S = 60


def disparar_sincronizacion_bunker() -> None:
    """Si defines BUNKER_SYNC_CMD, se ejecuta tras un cambio en el reporte (ej. `python v10_terminal.py`)."""
    cmd = os.environ.get("BUNKER_SYNC_CMD", "").strip()
    if not cmd:
        return
    print(f"⚙️  BUNKER_SYNC_CMD: {cmd[:80]}{'…' if len(cmd) > 80 else ''}")
    subprocess.run(cmd, shell=True, check=False)


def vigilancia_silenciosa(
    reporte_path: str = REPORTE_DEFAULT,
    intervalo_s: int = INTERVALO_S,
) -> None:
    print("🦚 Agente @Pau en modo vigilancia... (V de Victoria)")
    ultima_m = None

    while True:
        try:
            if os.path.exists(reporte_path):
                m = os.path.getmtime(reporte_path)
                if ultima_m is None:
                    ultima_m = m
                elif m > ultima_m:
                    ultima_m = m
                    print("✨ Detectada actualización de estrategia. Sincronizando búnker...")
                    disparar_sincronizacion_bunker()
            time.sleep(intervalo_s)
        except KeyboardInterrupt:
            print("\n🛑 Vigilancia detenida.")
            break


if __name__ == "__main__":
    vigilancia_silenciosa()
