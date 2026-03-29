import json
import os

class TryOnYouSovereignty:
    def __init__(self):
        self.project_id = "gen-lang-client-0091228222"
        self.founder = "Ruben Espinar Rodriguez"
        self.patent = "PCT/EP2025/067317"
        self.siret = "94361019600017"
        self.org = "Tryonme-com"
        
    def sync_all(self):
        print(f"--- CONSOLIDANDO TODO EN {self.project_id} ---")
        
        # 1. Generar Manifiesto Legal Único
        manifest = {
            "metadata": {
                "founder": self.founder,
                "patent": self.patent,
                "siret": self.siret,
                "org": self.org
            },
            "features": ["Mirror_Overlay_V10", "Stripe_Secure_Link", "VIP_QR_Reservation"],
            "status": "PRODUCTION_READY"
        }
        
        with open('production_manifest.json', 'w') as f:
            json.dump(manifest, f, indent=4)
        print("✅ production_manifest.json consolidado.")

        # 2. Forzar subida de todos los cambios pendientes a la Organización
        print("Subiendo blindaje a GitHub...")
        os.system("git add .")
        os.system(f"git commit -m 'Consolidacion Total V10 - Founder: {self.founder}'")
        os.system("git push origin magia-dorada-25e9d --force")
        
        print(f"\n--- EXITO: Todo el conocimiento volcado en tryonyou-app ---")

if __name__ == "__main__":
    app = TryOnYouSovereignty()
    app.sync_all()
