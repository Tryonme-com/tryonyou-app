import os

# Rutas de la estructura React
HOOKS_DIR = "src/hooks"
ANALYTICS_FILE = os.path.join(HOOKS_DIR, "useOmegaAnalytics.js")

def generar_modulo_telemetria():
    print("=== INICIANDO DESPLIEGUE DE TELEMETRÍA OMEGA (AGENTE 70) ===")
    
    if not os.path.exists(HOOKS_DIR):
        os.makedirs(HOOKS_DIR)
        print(f"📁 Directorio {HOOKS_DIR} creado.")

    hook_code = """
import { useCallback } from 'react';

export const useOmegaAnalytics = () => {
  const trackConversionEvent = useCallback((eventName, referenceId, priceTTC) => {
    const timestamp = new Date().toISOString();
    console.table([{ 
        EVENTO: eventName, 
        REFERENCIA: referenceId, 
        IMPORTE_TTC: `€${priceTTC}`, 
        HORA: timestamp 
    }]);
  }, []);

  const trackAddToCart = (referenceId, priceTTC) => trackConversionEvent('ADD_TO_CART', referenceId, priceTTC);
  return { trackAddToCart };
};
"""
    try:
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            f.write(hook_code.strip())
        print(f"✅ Módulo de telemetría inyectado en: {ANALYTICS_FILE}")
        print("=== PIPELINE DE DATOS PREPARADO ===")
    except Exception as e:
        print(f"❌ Error al generar el módulo: {e}")

if __name__ == "__main__":
    generar_modulo_telemetria()