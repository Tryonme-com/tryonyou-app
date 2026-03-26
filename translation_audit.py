import json
import os

def get_refined_parisian_tone(text, lang):
    """
    Aplica el tono 'Refined Parisian Eric Persona' a las cadenas de la UI.
    Tono: Elegante, minimalista, seguro, sofisticado y directo.
    """
    translations = {
        "fr": {
            "Reservar en Probador": "Réserver en Salon d'Essayage",
            "Mi Selección Perfecta": "Ma Sélection Signature",
            "scanning": "Analyse de la silhouette en cours...",
            "success": "Ajustement haute précision validé.",
            "error": "Écart biométrique détecté. Veuillez ajuster la posture.",
            "brand_fallback": "L'élégance Burberry en alternative d'exception."
        },
        "en": {
            "Reservar en Probador": "Reserve in Fitting Suite",
            "Mi Selección Perfecta": "My Signature Selection",
            "scanning": "Biometric silhouette analysis...",
            "success": "High-precision fit validated.",
            "error": "Biometric variance detected. Please adjust posture.",
            "brand_fallback": "Burberry elegance as an exceptional alternative."
        },
        "es": {
            "Reservar en Probador": "Reservar en Salón de Probadores",
            "Mi Selección Perfecta": "Mi Selección de Autor",
            "scanning": "Analizando silueta biométrica...",
            "success": "Ajuste de alta precisión validado.",
            "error": "Variación biométrica detectada. Ajuste su postura.",
            "brand_fallback": "Elegancia Burberry como alternativa de excepción."
        }
    }
    return translations.get(lang, {}).get(text, text)

def audit_translations():
    print("🖋️ Iniciando Auditoría de Traducciones: Tono 'Refined Parisian Eric Persona'...")
    
    ui_elements = ["Reservar en Probador", "Mi Selección Perfecta", "scanning", "success", "error", "brand_fallback"]
    languages = ["fr", "en", "es"]
    
    audit_results = {}
    
    for lang in languages:
        print(f"  🌐 Procesando idioma: {lang.upper()}")
        lang_results = {}
        for element in ui_elements:
            refined_text = get_refined_parisian_tone(element, lang)
            lang_results[element] = refined_text
        audit_results[lang] = lang_results

    # Guardar resultados de la auditoría
    with open("translation_audit_results.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
        
    print("✅ Auditoría completada. Resultados guardados en: translation_audit_results.json")
    
    # Generar archivo de locales para el frontend
    locales_content = "export const Locales = " + json.dumps(audit_results, indent=2, ensure_ascii=False) + ";"
    with open("tryonyou-app/src/locales/refined_locales.ts", "w", encoding="utf-8") as f:
        f.write(locales_content)
    print("🚀 Archivo de locales generado: src/locales/refined_locales.ts")

if __name__ == "__main__":
    audit_translations()
