import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { SALES_COPY, type AppLocale } from "../locales/salesCopy";

type PauGuideStep = "idle" | "greeting" | "scanning" | "snapping" | "showing";

type PauFloatingGuideProps = {
  locale: AppLocale;
};

const PARTICLE_COUNT = 20;

export function PauFloatingGuide({ locale }: PauFloatingGuideProps) {
  const copy = SALES_COPY[locale];
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState<PauGuideStep>("idle");
  const [snapCount, setSnapCount] = useState(0);
  const [burstKey, setBurstKey] = useState(0);

  const particles = useMemo(
    () =>
      Array.from({ length: PARTICLE_COUNT }, (_, index) => {
        const angle = (360 / PARTICLE_COUNT) * index;
        const distance = 54 + (index % 5) * 14;
        const delay = index * 0.025;
        return {
          id: `particle-${index}`,
          angle,
          distance,
          delay,
          duration: 0.9 + (index % 3) * 0.15,
        };
      }),
    [],
  );

  useEffect(() => {
    if (!isOpen) {
      setStep("idle");
      return;
    }
    if (step !== "idle") return;
    setStep("greeting");
  }, [isOpen, step]);

  useEffect(() => {
    if (!isOpen) return;

    if (step === "greeting") {
      const timer = window.setTimeout(() => setStep("scanning"), 1800);
      return () => window.clearTimeout(timer);
    }

    if (step === "snapping") {
      const timer = window.setTimeout(() => setStep("showing"), 1100);
      return () => window.clearTimeout(timer);
    }

    return undefined;
  }, [isOpen, step]);

  const visibleMessages = [
    copy.pauGuideGreeting,
    copy.pauGuideWelcome,
    step === "scanning" || step === "snapping" || step === "showing"
      ? copy.pauGuideScan
      : null,
    step === "snapping" || step === "showing"
      ? snapCount > 1
        ? copy.pauGuideNext
        : copy.pauGuideSnap
      : null,
    step === "showing" ? copy.pauGuideClosing : null,
  ].filter(Boolean) as string[];

  const handleToggle = () => {
    if (isOpen) {
      setIsOpen(false);
      setStep("idle");
      return;
    }
    setIsOpen(true);
    setStep("greeting");
  };

  const handleSnap = () => {
    if (step === "greeting") return;
    setBurstKey((value) => value + 1);
    setSnapCount((value) => value + 1);
    setStep("snapping");
  };

  return (
    <div
      className="pau-guide-shell"
      aria-live="polite"
      data-open={isOpen ? "1" : undefined}
      data-step={step}
    >
      <AnimatePresence>
        {isOpen ? (
            <motion.aside
              key="pau-guide-panel"
              className="pau-guide-panel"
              data-step={step}
              initial={{ opacity: 0, y: 20, scale: 0.96 }}

            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 18, scale: 0.96 }}
            transition={{ duration: 0.28, ease: "easeOut" }}
          >
            <span className="pau-guide-panel__shimmer" aria-hidden="true" />
            <div className="pau-guide-panel__header">
              <div className="pau-guide-panel__identity">
                <div className="pau-guide-avatar pau-guide-avatar--panel">
                  <video autoPlay loop muted playsInline preload="auto">
                    <source src="/videos/pau_transparent.webm" type="video/webm" />
                    <source src="/videos/pau_transparent.mp4" type="video/mp4" />
                  </video>
                </div>
                <div>
                  <p className="pau-guide-panel__eyebrow">P.A.U.</p>
                  <p className="pau-guide-panel__title">Maison Digitale</p>
                </div>
              </div>
              <button
                type="button"
                className="pau-guide-close"
                onClick={handleToggle}
                aria-label="Fermer l'assistant P.A.U."
              >
                ×
              </button>
            </div>

            <div className="pau-guide-thread">
              {visibleMessages.map((message, index) => (
                <motion.div
                  key={`${message}-${index}`}
                  className="pau-guide-bubble"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.28, delay: index * 0.06 }}
                >
                  {message}
                </motion.div>
              ))}
            </div>

            <div className="pau-guide-look-card" data-active={step === "showing" ? "1" : undefined}>
              <div className="pau-guide-look-card__halo" />
              <div className="pau-guide-look-card__figure" />
              <div className="pau-guide-look-card__ribbon" />
              <div className="pau-guide-look-card__glow" />
              <div className="pau-guide-particles" key={burstKey} data-active={step === "snapping" ? "1" : undefined}>
                {particles.map((particle) => (
                  <span
                    key={particle.id}
                    className="pau-guide-particle"
                    style={{
                      "--angle": `${particle.angle}deg`,
                      "--distance": `${particle.distance}px`,
                      "--delay": `${particle.delay}s`,
                      "--duration": `${particle.duration}s`,
                    } as React.CSSProperties}
                  />
                ))}
              </div>
            </div>

            <div className="pau-guide-actions">
              <button
                type="button"
                className="pau-guide-snap"
                onClick={handleSnap}
                disabled={step === "greeting" || step === "snapping"}
              >
                THE SNAP
              </button>
            </div>
          </motion.aside>
        ) : null}
      </AnimatePresence>

      <motion.button
        type="button"
        className="pau-guide-trigger"
        data-open={isOpen ? "1" : undefined}
        onClick={handleToggle}
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.98 }}
        aria-label="Ouvrir l'assistant flottant P.A.U."
        aria-pressed={isOpen}
      >
        <span className="pau-guide-trigger__pulse" aria-hidden="true" />
        <span className="pau-guide-trigger__ring" />
        <span className="pau-guide-avatar">
          <video autoPlay loop muted playsInline preload="auto">
            <source src="/videos/pau_transparent.webm" type="video/webm" />
            <source src="/videos/pau_transparent.mp4" type="video/mp4" />
          </video>
        </span>
      </motion.button>
    </div>
  );
}
