import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useMirrorEngine, type GarmentSuggestion } from "../hooks/useMirrorEngine";
import { buildCoreHeaders, ensureMirrorSessionId, resolveAccountScope } from "../lib/coreEngineClient";
import { ORO_DIVINEO } from "../divineo/divineoV11Config";
import type { AppLocale } from "../locales/salesCopy";

type MirrorCopy = {
  title: string;
  scanning: string;
  selectPerfect: string;
  reserveCabin: string;
  viewCombinations: string;
  saveSilhouette: string;
  shareLook: string;
  balmainTrigger: string;
  scanCta: string;
  noSuggestions: string;
  qrGenerated: string;
  silhouetteSaved: string;
  shareGenerated: string;
  lookAdded: string;
};

const MIRROR_COPY: Record<AppLocale, MirrorCopy> = {
  fr: {
    title: "Miroir Digital",
    scanning: "Analyse biométrique en cours…",
    selectPerfect: "Ma Sélection Parfaite",
    reserveCabin: "Réserver en Cabine",
    viewCombinations: "Voir les Combinaisons",
    saveSilhouette: "Enregistrer ma Silhouette",
    shareLook: "Partager le Look",
    balmainTrigger: "Balmain",
    scanCta: "Lancer le scan",
    noSuggestions: "Lancez le scan pour découvrir vos 5 suggestions.",
    qrGenerated: "QR cabine généré — réservation confirmée.",
    silhouetteSaved: "Silhouette enregistrée sous protocole chiffré.",
    shareGenerated: "Image de partage générée (données biométriques supprimées).",
    lookAdded: "Look ajouté à votre sélection avec la taille calculée.",
  },
  en: {
    title: "Digital Mirror",
    scanning: "Biometric analysis in progress…",
    selectPerfect: "My Perfect Selection",
    reserveCabin: "Reserve Fitting Room",
    viewCombinations: "View Combinations",
    saveSilhouette: "Save My Silhouette",
    shareLook: "Share the Look",
    balmainTrigger: "Balmain",
    scanCta: "Start scan",
    noSuggestions: "Start the scan to discover your 5 suggestions.",
    qrGenerated: "Fitting room QR generated — reservation confirmed.",
    silhouetteSaved: "Silhouette saved under encrypted protocol.",
    shareGenerated: "Share image generated (biometric data stripped).",
    lookAdded: "Look added to your selection with calculated size.",
  },
  es: {
    title: "Espejo Digital",
    scanning: "Análisis biométrico en curso…",
    selectPerfect: "Mi Selección Perfecta",
    reserveCabin: "Reservar en Probador",
    viewCombinations: "Ver las Combinaciones",
    saveSilhouette: "Guardar mi Silueta",
    shareLook: "Compartir el Look",
    balmainTrigger: "Balmain",
    scanCta: "Iniciar escaneo",
    noSuggestions: "Inicia el escaneo para descubrir tus 5 sugerencias.",
    qrGenerated: "QR de probador generado — reserva confirmada.",
    silhouetteSaved: "Silueta guardada bajo protocolo cifrado.",
    shareGenerated: "Imagen de compartir generada (datos biométricos eliminados).",
    lookAdded: "Look añadido a tu selección con la talla calculada.",
  },
};

type Props = {
  locale: AppLocale;
  visible: boolean;
  onClose: () => void;
};

export function DigitalMirrorPanel({ locale, visible, onClose }: Props) {
  const copy = MIRROR_COPY[locale];
  const engine = useMirrorEngine();
  const [viewingAll, setViewingAll] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const showFeedback = (msg: string) => {
    setFeedback(msg);
    setTimeout(() => setFeedback(null), 3500);
  };

  const handleScan = useCallback(() => {
    void engine.triggerScan("soirée");
  }, [engine]);

  const handleBalmain = useCallback(async () => {
    await engine.triggerBalmainSnap();
  }, [engine]);

  const handleSelectPerfect = useCallback(async () => {
    if (!engine.activeLook) return;
    try {
      const response = await fetch("/api/v1/pau/perfect-selection", {
        method: "POST",
        headers: buildCoreHeaders(),
        body: JSON.stringify({
          session_id: ensureMirrorSessionId(),
          account_scope: resolveAccountScope(),
          look_data: {
            id: engine.activeLook.id,
            name: engine.activeLook.name,
            price: engine.activeLook.price,
          },
        }),
        credentials: "same-origin",
      });
      if (response.ok) {
        showFeedback(copy.lookAdded);
      }
    } catch { /* offline */ }
  }, [engine.activeLook, copy.lookAdded]);

  const handleReserveCabin = useCallback(async () => {
    if (!engine.activeLook) return;
    try {
      const response = await fetch("/api/v1/pau/reserve", {
        method: "POST",
        headers: buildCoreHeaders(),
        body: JSON.stringify({
          session_id: ensureMirrorSessionId(),
          account_scope: resolveAccountScope(),
          look_id: engine.activeLook.id,
        }),
        credentials: "same-origin",
      });
      if (response.ok) {
        showFeedback(copy.qrGenerated);
      }
    } catch { /* offline */ }
  }, [engine.activeLook, copy.qrGenerated]);

  const handleViewCombinations = useCallback(() => {
    setViewingAll(true);
    if (engine.activeLook && engine.suggestions.length > 0) {
      void engine.triggerSnap(engine.suggestions[1]?.id);
    }
  }, [engine]);

  const handleSaveSilhouette = useCallback(async () => {
    try {
      const response = await fetch("/api/v1/mirror/save-silhouette", {
        method: "POST",
        headers: buildCoreHeaders(),
        body: JSON.stringify({
          session_id: ensureMirrorSessionId(),
          account_scope: resolveAccountScope(),
          protocol: "zero_size_encrypted",
        }),
        credentials: "same-origin",
      });
      if (response.ok) {
        showFeedback(copy.silhouetteSaved);
      }
    } catch { /* offline */ }
  }, [copy.silhouetteSaved]);

  const handleShareLook = useCallback(async () => {
    try {
      const response = await fetch("/api/v1/mirror/share-look", {
        method: "POST",
        headers: buildCoreHeaders(),
        body: JSON.stringify({
          session_id: ensureMirrorSessionId(),
          account_scope: resolveAccountScope(),
          look_id: engine.activeLook?.id ?? null,
          strip_biometric: true,
        }),
        credentials: "same-origin",
      });
      if (response.ok) {
        showFeedback(copy.shareGenerated);
      }
    } catch { /* offline */ }
  }, [engine.activeLook, copy.shareGenerated]);

  const displayedSuggestions: GarmentSuggestion[] = viewingAll
    ? engine.suggestions
    : engine.suggestions.slice(0, 1);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="mirror-panel"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 30 }}
          transition={{ duration: 0.4 }}
        >
          <div className="mirror-panel__header">
            <h2 style={{ color: ORO_DIVINEO, margin: 0 }}>{copy.title}</h2>
            <button
              type="button"
              className="mirror-panel__close"
              onClick={onClose}
              aria-label="Close"
            >
              &times;
            </button>
          </div>

          {engine.scanning && (
            <div className="mirror-panel__scanning">
              <motion.div
                className="mirror-panel__pulse"
                animate={{ scale: [1, 1.2, 1], opacity: [0.6, 1, 0.6] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
              <p>{copy.scanning}</p>
            </div>
          )}

          {!engine.scanComplete && !engine.scanning && (
            <div className="mirror-panel__empty">
              <p>{copy.noSuggestions}</p>
              <button
                type="button"
                className="button button--primary"
                onClick={handleScan}
              >
                {copy.scanCta}
              </button>
            </div>
          )}

          {engine.scanComplete && engine.suggestions.length > 0 && (
            <>
              <div className="mirror-panel__suggestions">
                {displayedSuggestions.map((look) => (
                  <motion.article
                    key={look.id}
                    className={`mirror-suggestion ${engine.activeLook?.id === look.id ? "mirror-suggestion--active" : ""}`}
                    onClick={() => {
                      engine.selectLook(look);
                      void engine.triggerSnap(look.id);
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="mirror-suggestion__name">{look.name}</span>
                    <span className="mirror-suggestion__price">
                      {new Intl.NumberFormat(locale, { style: "currency", currency: "EUR" }).format(look.price)}
                    </span>
                    <span className="mirror-suggestion__fit">{look.fit_profile}</span>
                  </motion.article>
                ))}
              </div>

              <div className="mirror-panel__actions">
                <button
                  type="button"
                  className="button button--primary mirror-action"
                  onClick={() => void handleSelectPerfect()}
                >
                  {copy.selectPerfect}
                </button>
                <button
                  type="button"
                  className="button button--secondary mirror-action"
                  onClick={() => void handleReserveCabin()}
                >
                  {copy.reserveCabin}
                </button>
                <button
                  type="button"
                  className="button button--secondary mirror-action"
                  onClick={handleViewCombinations}
                >
                  {copy.viewCombinations}
                </button>
                <button
                  type="button"
                  className="button button--secondary mirror-action"
                  onClick={() => void handleSaveSilhouette()}
                >
                  {copy.saveSilhouette}
                </button>
                <button
                  type="button"
                  className="button button--secondary mirror-action"
                  onClick={() => void handleShareLook()}
                >
                  {copy.shareLook}
                </button>
              </div>

              <div className="mirror-panel__brand-triggers">
                <button
                  type="button"
                  className="button button--balmain mirror-brand"
                  onClick={() => void handleBalmain()}
                >
                  {copy.balmainTrigger}
                </button>
              </div>
            </>
          )}

          <AnimatePresence>
            {feedback && (
              <motion.div
                className="mirror-panel__feedback"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                role="status"
              >
                {feedback}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
