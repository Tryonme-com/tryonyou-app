/**
 * Carga la configuración maestra V10 desde GCS (u otra URL pública).
 *
 * mirror_ui/.env.local (opcional):
 *   VITE_V10_CONFIG_URL=https://storage.googleapis.com/tryonyou-production-v10/v10_core_config.json
 */

const DEFAULT_V10_CONFIG_URL =
  "https://storage.googleapis.com/tryonyou-production-v10/v10_core_config.json";

export const fetchV10Config = async () => {
  const url =
    import.meta.env.VITE_V10_CONFIG_URL?.trim() || DEFAULT_V10_CONFIG_URL;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`V10 config HTTP ${response.status}: ${response.statusText}`);
    }
    const config = await response.json();
    console.log("💎 TryOnYou V10 sincronizada:", config?.metadata?.status);
    return config;
  } catch (error) {
    console.error("❌ Error de sincronización con el búnker:", error);
    return null;
  }
};
