/**
 * Visual Certainty — Protocolo Divineo V10
 * Muestra un overlay de confirmación visual antes de redirigir al checkout.
 */

export const triggerVisualCertainty = () => {
  // Prevent duplicate overlays
  const existing = document.getElementById('divineo-overlay');
  if (existing) return;

  const overlay = document.createElement('div');
  overlay.id = 'divineo-overlay';
  overlay.innerHTML = `
    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
                background: rgba(0,0,0,0.8); display: flex; align-items: center; 
                justify-content: center; z-index: 9999; border: 2px solid #D4AF37;">
      <h2 style="color: #D4AF37; font-family: serif; letter-spacing: 0.5em; text-transform: uppercase;">
        AJUSTE PERFECTO. COMPRANDO...
      </h2>
    </div>
  `;
  document.body.appendChild(overlay);

  // Auto-remove after a reasonable timeout in case checkout navigation doesn't unload the page
  window.setTimeout(() => {
    overlay.remove();
  }, 8000);
};
