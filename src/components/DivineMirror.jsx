import { useEffect } from 'react';

/**
 * DivineMirror — Espejo digital biométrico.
 * Listens for pose-fit events dispatched by the MediaPipe layer (index.html)
 * and forwards them to the parent component via onFitChange.
 */
export default function DivineMirror({ onFitChange }) {
  useEffect(() => {
    const onFit = (e) => {
      const lab = e.detail?.label;
      if (typeof lab === 'string' && lab.length > 0 && onFitChange) {
        onFitChange(lab);
      }
    };
    window.addEventListener('tryonyou:fit', onFit);
    return () => window.removeEventListener('tryonyou:fit', onFit);
  }, [onFitChange]);

  return (
    <div
      id="divine-mirror"
      aria-label="Divine Mirror — Espejo digital biométrico"
      role="region"
    />
  );
}
