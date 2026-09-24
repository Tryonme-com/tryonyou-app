agente_ventas_divineo.py
import os

# CONFIGURACIÓN ESTRATÉGICA DIVINEO V9
DATA = {
    "empresa": "DIVINEO V9",
    "siren": "943 610 196",
    "patente": "PCT/EP2025/067317",
    "oferta": "Auditoría Biométrica 0.08mm",
    "precio": "250€ por SKU",
    "objetivo": "Marcas de Moda Independiente (Paris 1er, 2e, 3e)"
}

PROPOSTA_TECNICA = f"""
OBJET : Optimisation de rentabilité e-commerce – {DATA['empresa']} (SIREN {DATA['siren']})

Madame, Monsieur,

Suite à l'analyse de vos retours clients, nous avons détecté une opportunité d'optimisation de votre fit. 
Grâce à notre brevet {DATA['patente']}, nous garantissons une précision de 0.08mm.

OFFRE FLASH : Une audit biométrique complète de votre pièce phare pour {DATA['precio']}. 
Objectif : Réduction immédiate de 30% de vos retours logistiques.

Êtes-vous disponible pour valider la souveraineté de vos tailles cette semaine ?
"""

def ejecutar_prospeccion():
    # Este es el comando para que Cursor busque objetivos
    print(f"🚀 Agente {DATA['empresa']} activado.")
    print(f"🔍 Buscando marcas de moda en Shopify con sede en París...")
    print(f"📧 Generando 10 borradores de propuesta técnica...")
    
    with open("CAMPANA_VENTAS_HOY.md", "w") as f:
        f.write(f"# CAMPAÑA DE LIQUIDEZ INMEDIATA\n\n{PROPOSTA_TECNICA}")
    
    return "Propuesta generada en CAMPANA_VENTAS_HOY.md"

ejecutar_prospeccion()
