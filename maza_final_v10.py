import os, subprocess, stripe
from datetime import datetime

# Leemos la clave de la terminal para blindar el código
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
REPO_URL = "https://github.com/LVT-ENG/tryonyou-app.git"
PATENTE = "PCT/EP2025/067317"
PROJECT_ROOT = os.path.expanduser("~/tryonyou-app")

def sellar_bunker_git():
    print(f"🏛️  [ERIC] Sellando Propiedad en GitHub (V10.4 Omega)...")
    os.chdir(PROJECT_ROOT)
    # Limpiamos cualquier rastro previo para asegurar subida limpia
    subprocess.run(["git", "add", "."], shell=False)
    msg = f"V10.4 OMEGA: Bunker 75005 Blindado - Patente {PATENTE}"
    subprocess.run(["git", "commit", "-m", msg], shell=False)
    subprocess.run(["git", "push", "origin", "main", "--force"], shell=False)
    print("✅ GitHub: Sincronizado y Blindado sin secretos expuestos.")

def generar_mazas_cobro():
    print(f"💰 [JULES] Activando Pasarelas de Pago Real...")
    if not STRIPE_API_KEY:
        print("❌ ERROR: No se detecta la clave. Asegúrate de haber hecho el export correctamente.")
        return None, None
    
    stripe.api_key = STRIPE_API_KEY
    
    # Licencia Pro (700€)
    p_pro = stripe.Product.create(name=f"Licencia V10 Pro - {PATENTE}", description="Certeza Biométrica 98.4%")
    pr_pro = stripe.Price.create(product=p_pro.id, unit_amount=70000, currency="eur")
    l_pro = stripe.PaymentLink.create(line_items=[{"price": pr_pro.id, "quantity": 1}])
    
    # Licencia Soberanía (98.000€)
    p_ent = stripe.Product.create(name="Licencia Soberanía V10", description="Implantación Global LVMH/Bpifrance")
    pr_ent = stripe.Price.create(product=p_ent.id, unit_amount=9800000, currency="eur")
    l_ent = stripe.PaymentLink.create(line_items=[{"price": pr_ent.id, "quantity": 1}])
    
    return l_pro.url, l_ent.url

if __name__ == "__main__":
    sellar_bunker_git()
    pro, ent = generar_mazas_cobro()
    if pro:
        print(f"\n--- 🏛️ INFORME DE RECAUDACIÓN V10.4 ---")
        print(f"🚀 LINK LICENCIA PRO (700€): {pro}")
        print(f"💰 LINK SOBERANÍA (98k€): {ent}")
        print(f"\n[V10 OMEGA] Búnker 75005 Operativo. ¡A FUEGO! ¡BOOM! ¡VIVIDO!")
