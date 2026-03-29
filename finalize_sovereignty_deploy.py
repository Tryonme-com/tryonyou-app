import json
import os

def seal_and_sync():
    print("\n--- INICIANDO SELLADO DE SOBERANIA v10 ---")
    
    metadata = {
        "founder": "Ruben Espinar Rodriguez",
        "patent": "PCT/EP2025/067317",
        "siret": "94361019600017",
        "project_id": "gen-lang-client-0091228222",
        "branch": "magia-dorada-25e9d"
    }

    with open('production_manifest.json', 'w') as f:
        json.dump(metadata, f, indent=4)
    print("✅ Manifiesto generado en tryonyou-app.")

    print("Conectando con el repositorio y subiendo cambios...")
    os.system("git add production_manifest.json")
    os.system("git commit -m 'Final seal: Sovereignty Protocol Active'")
    
    # Intento de push a la organización
    result = os.system("git push origin magia-dorada-25e9d")
    
    if result == 0:
        print("\n--- EXITO REAL: Proyecto sincronizado y blindado ---")
        print("La firma de Ruben y la patente ya estan en la nube.")
    else:
        print("\n❌ Error en el Push. Verifica que el 'origin' sea Tryonme-com.")

if __name__ == "__main__":
    seal_and_sync()
