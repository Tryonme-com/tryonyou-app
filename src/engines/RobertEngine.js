/** 🛡️ CONFIGURACIÓN SOBERANA DEL MOTOR */
const engineConfig = {
  mode: import.meta.env.VITE_ENGINE_MODE || 'STANDARD',
  precision: parseFloat(import.meta.env.VITE_PRECISION_LEVEL || '0.5'),
  overlay: import.meta.env.VITE_OVERLAY_SYNC?.toUpperCase() === 'TRUE'
};

console.log(`🔱 MOTOR INICIALIZADO EN MODO: ${engineConfig.mode}`);

export default engineConfig;
