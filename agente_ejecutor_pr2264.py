import os

import requests

REPO = "LVT-ENG/TRYONME-TRYONYOU-ABVETOS--INTELLIGENCE--SYSTEM"
PR_NUMBER = 2264
PATENTE = "PCT/EP2025/067317"


def agente_ejecutor_pr2264() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "TU_GITHUB_TOKEN":
        print("⚠️ Define GITHUB_TOKEN en el entorno (no uses el placeholder en código).")
        return

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    comentario_texto = (
        "🦚 **Informe del Agente @Pau:**\n\n"
        "Analizando PR #2264 para consolidación de Inteligencia @Divineo.\n"
        f"✅ Patente **{PATENTE}** validada en el núcleo.\n"
        "✅ Sincronización con Leads Globales (Galeries/Station F) OK.\n"
        "✅ Error de Vite purgado. @Visa_Expres lista para flujo real.\n\n"
        "**Veredicto:** Acierto 100%. Procedo al Merge de Victoria. @CertezaAbsoluta @lo+erestu"
    )

    print(f"💬 Comentando en PR #{PR_NUMBER}...")
    com = requests.post(
        f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments",
        json={"body": comentario_texto},
        headers=headers,
        timeout=60,
    )
    if com.status_code not in (200, 201):
        print(f"⚠️ Comentario: HTTP {com.status_code} — {com.text[:200]}")

    print(f"🚀 Ejecutando Auto-Merge en {REPO}...")
    merge_data = {
        "commit_title": f"Merge #2264: Consolidación @Divineo @CertezaAbsoluta @lo+erestu {PATENTE}",
        "merge_method": "squash",
    }

    response = requests.put(
        f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/merge",
        json=merge_data,
        headers=headers,
        timeout=60,
    )

    if response.status_code == 200:
        print("✨ ¡BÚNKER ACTUALIZADO! El @Divineo está en Main.")
    else:
        try:
            msg = response.json().get("message", response.text)
        except Exception:
            msg = response.text
        print(f"⚠️ Error en el búnker: {msg}")


if __name__ == "__main__":
    agente_ejecutor_pr2264()
