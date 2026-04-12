import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

type Props = {
  visible: boolean;
  onDismiss: () => void;
};

const LINES = [
  "Plus de 5\u202f000 références.",
  "Seulement 5 sélections parfaites.",
  "L\u2019élégance n\u2019est pas une question de quantité,\u00a0mais de certitude.",
] as const;

const AUTO_DISMISS_MS = 7000;

/**
 * PreScanHook — full-screen luxury teaser shown once before the scan begins.
 * Dismisses automatically after AUTO_DISMISS_MS, or immediately on user action.
 */
export function PreScanHook({ visible, onDismiss }: Props) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!visible) return;
    timerRef.current = setTimeout(onDismiss, AUTO_DISMISS_MS);
    return () => {
      if (timerRef.current !== null) clearTimeout(timerRef.current);
    };
  }, [visible, onDismiss]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="pre-scan-hook"
          role="dialog"
          aria-modal="true"
          aria-label="Message d'introduction — avant le scan"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.7, ease: "easeInOut" }}
        >
          <div className="pre-scan-hook__inner">
            <div className="pre-scan-hook__bar" aria-hidden />

            <div className="pre-scan-hook__lines">
              {LINES.map((line, i) => (
                <motion.p
                  key={line}
                  className={
                    i === LINES.length - 1
                      ? "pre-scan-hook__line pre-scan-hook__line--accent"
                      : "pre-scan-hook__line"
                  }
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.35 + i * 0.28 }}
                >
                  {line}
                </motion.p>
              ))}
            </div>

            <motion.button
              type="button"
              className="pre-scan-hook__cta"
              onClick={onDismiss}
              aria-label="Commencer le scan"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 1.45 }}
            >
              Commencer
            </motion.button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
