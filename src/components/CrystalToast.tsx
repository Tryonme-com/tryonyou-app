import { useEffect } from "react";

type Props = {
  message: string | null;
  onClose: () => void;
  durationMs?: number;
};

/**
 * Retour discret luxury (verre / or) — pas de alert() bloquant.
 */
export function CrystalToast({ message, onClose, durationMs = 5200 }: Props) {
  useEffect(() => {
    if (!message) return;
    const id = window.setTimeout(onClose, durationMs);
    return () => window.clearTimeout(id);
  }, [message, onClose, durationMs]);

  if (!message) return null;

  return (
    <div
      className="crystal-toast-wrap"
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="crystal-toast">
        <p className="crystal-toast-text">{message}</p>
        <button
          type="button"
          className="crystal-toast-close"
          onClick={onClose}
          aria-label="Fermer le message"
        >
          ×
        </button>
      </div>
    </div>
  );
}
