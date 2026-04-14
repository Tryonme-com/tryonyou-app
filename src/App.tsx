import { type FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion, useInView } from "framer-motion";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import { PauFloatingGuide } from "./components/PauFloatingGuide";
import { PreScanHook } from "./components/PreScanHook";
import { SALES_COPY, SUPPORTED_LOCALES, type AppLocale } from "./locales/salesCopy";
import "./index.css";
import "./App.css";

type DemoFormState = {
  fullName: string;
  corporateEmail: string;
  company: string;
  role: string;
  businessType: string;
  primaryMarket: string;
  challenge: string;
  volume: string;
  horizon: string;
  consent: boolean;
};

type SubmitState = "idle" | "submitting" | "success" | "error";

const DEFAULT_FORM_STATE: DemoFormState = {
  fullName: "",
  corporateEmail: "",
  company: "",
  role: "",
  businessType: "",
  primaryMarket: "",
  challenge: "",
  volume: "",
  horizon: "",
  consent: false,
};

const AMBIENT_PARTICLES = Array.from({ length: 22 }, (_, index) => ({
  id: `particle-${index}`,
  left: `${(index * 4.4 + 6) % 100}%`,
  size: `${10 + (index % 6) * 5}px`,
  delay: `${(index % 7) * 1.35}s`,
  duration: `${14 + (index % 5) * 3}s`,
}));

function getInitialLocale(): AppLocale {
  if (typeof window === "undefined") return "fr";
  const stored = window.localStorage.getItem("tryonyou-locale");
  if (stored === "fr" || stored === "en" || stored === "es") return stored;

  const language = window.navigator.language.toLowerCase();
  if (language.startsWith("es")) return "es";
  if (language.startsWith("en")) return "en";
  return "fr";
}

function localeTag(locale: AppLocale): string {
  if (locale === "fr") return "fr-FR";
  if (locale === "en") return "en-GB";
  return "es-ES";
}

function formatMetricValue(locale: AppLocale, index: number, value: number): string {
  const numberLocale = localeTag(locale);

  if (index === 0) {
    return `-${new Intl.NumberFormat(numberLocale, { maximumFractionDigits: 0 }).format(value)}${locale === "en" ? "%" : " %"}`;
  }

  if (index === 1) {
    return `${new Intl.NumberFormat(numberLocale, {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(value)}${locale === "en" ? "%" : " %"}`;
  }

  return new Intl.NumberFormat(numberLocale, { maximumFractionDigits: 0 }).format(value);
}

function MetricCounter({
  locale,
  index,
  fallback,
}: {
  locale: AppLocale;
  index: number;
  fallback: string;
}) {
  const ref = useRef<HTMLSpanElement | null>(null);
  const isInView = useInView(ref, { once: true, amount: 0.55 });
  const [display, setDisplay] = useState(index === 3 ? fallback : formatMetricValue(locale, index, 0));

  useEffect(() => {
    if (index === 3) {
      setDisplay(fallback);
      return;
    }

    if (!isInView) return;

    const targets = [85, 99.7, 10000] as const;
    const target = targets[index] ?? 0;
    const duration = 1200;
    let frame = 0;
    const start = performance.now();

    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const nextValue = target * eased;
      setDisplay(formatMetricValue(locale, index, nextValue));
      if (progress < 1) {
        frame = window.requestAnimationFrame(tick);
      }
    };

    frame = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(frame);
  }, [fallback, index, isInView, locale]);

  return <span ref={ref}>{display}</span>;
}

function App() {
  const [locale, setLocale] = useState<AppLocale>(getInitialLocale);
  const [formState, setFormState] = useState<DemoFormState>(DEFAULT_FORM_STATE);
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [pilotPreviewOpen, setPilotPreviewOpen] = useState(false);
  const [preScanVisible, setPreScanVisible] = useState(false);

  const copy = SALES_COPY[locale];

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem("tryonyou-locale", locale);
  }, [locale]);

  const navigationLinks = useMemo(
    () => [
      { label: copy.nav.home, href: "#home" },
      { label: copy.nav.technology, href: "#technology" },
      { label: copy.nav.solutions, href: "#solutions" },
      { label: copy.nav.pilots, href: "#pilots" },
      { label: copy.nav.about, href: "#about" },
      { label: copy.nav.legal, href: "#legal" },
    ],
    [copy.nav],
  );

  const updateField = <K extends keyof DemoFormState>(key: K, value: DemoFormState[K]) => {
    setFormState((current) => ({ ...current, [key]: value }));
  };

  const handlePilotLaunch = () => {
    setPilotPreviewOpen(true);
    setPreScanVisible(true);
  };

  const handlePilotAction = async (action: OfrendaKey) => {
    try {
      await fetch("/api/v1/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          intent: `pilot_${action}`,
          source: "landing_pilot_preview",
          protocol: "zero_size",
        }),
      });
    } catch {
      // Silent by design: the pilot preview is illustrative and should not block the page.
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!formState.consent) {
      setSubmitState("error");
      return;
    }

    setSubmitState("submitting");

    const message = [
      `${copy.demoForm.fieldLabels.businessType}: ${formState.businessType}`,
      `${copy.demoForm.fieldLabels.primaryMarket}: ${formState.primaryMarket}`,
      `${copy.demoForm.fieldLabels.challenge}: ${formState.challenge}`,
      formState.volume
        ? `${copy.demoForm.fieldLabels.volume}: ${formState.volume}`
        : null,
      formState.horizon
        ? `${copy.demoForm.fieldLabels.horizon}: ${formState.horizon}`
        : null,
    ]
      .filter(Boolean)
      .join(" | ");

    try {
      const response = await fetch("/api/demo-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formState.fullName,
          email: formState.corporateEmail,
          company: formState.company,
          role: formState.role,
          catalog_size: formState.volume,
          message,
          source: "landing_demo_form_enterprise",
          locale,
          ts: new Date().toISOString(),
          business_type: formState.businessType,
          primary_market: formState.primaryMarket,
          challenge: formState.challenge,
          project_horizon: formState.horizon,
          consent: formState.consent,
        }),
      });

      if (!response.ok) {
        throw new Error("demo_request_failed");
      }

      setSubmitState("success");
      setFormState(DEFAULT_FORM_STATE);
    } catch {
      setSubmitState("error");
    }
  };

  return (
    <div className="app-shell">
      <div className="app-particles" aria-hidden="true">
        {AMBIENT_PARTICLES.map((particle) => (
          <span
            key={particle.id}
            className="app-particle"
            style={{
              left: particle.left,
              width: particle.size,
              height: particle.size,
              animationDelay: particle.delay,
              animationDuration: particle.duration,
            }}
          />
        ))}
      </div>

      <PreScanHook visible={preScanVisible} onDismiss={() => setPreScanVisible(false)} />

      <header className="site-header">
        <div className="site-header__inner">
          <a className="brand-lockup" href="#home" aria-label="TRYONYOU">
            <span className="brand-lockup__name">TRYONYOU</span>
            <span className="brand-lockup__product">Digital Fit Engine</span>
          </a>

          <nav className="site-nav" aria-label="Primary">
            {navigationLinks.map((link) => (
              <a key={link.href} href={link.href} className="site-nav__link">
                {link.label}
              </a>
            ))}
          </nav>

          <div className="site-header__actions">
            <div className="locale-switch" role="group" aria-label={copy.localeLabel}>
              {SUPPORTED_LOCALES.map((supportedLocale) => (
                <button
                  key={supportedLocale}
                  type="button"
                  className="locale-switch__button"
                  data-active={supportedLocale === locale ? "true" : undefined}
                  onClick={() => setLocale(supportedLocale)}
                >
                  {supportedLocale.toUpperCase()}
                </button>
              ))}
            </div>
            <a className="button button--primary button--compact" href="#demo">
              {copy.nav.demo}
            </a>
          </div>
        </div>
      </header>

      <main className="site-main">
        <motion.section
          id="home"
          className="section section--hero"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.25 }}
          transition={{ duration: 0.65, ease: "easeOut" }}
        >
          <div className="section-shell hero-grid">
            <div className="hero-copy">
              <p className="section-kicker">TRYONYOU · Digital Fit Engine</p>
              <h1>{copy.hero.title}</h1>
              <p className="section-lead">{copy.hero.lead}</p>
              <div className="hero-actions">
                <a className="button button--primary" href="#demo">
                  {copy.hero.cta}
                </a>
              </div>
            </div>

            <div className="hero-panel">
              <div className="hero-panel__inner">
                <p className="hero-panel__eyebrow">{copy.technology.pauLabel}</p>
                <h2>TRYONYOU</h2>
                <p>{copy.solution.support}</p>
                <ul className="module-list">
                  {copy.technology.modules.map((module) => (
                    <li key={module}>{module}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="section-shell">
            <div className="trust-strip" role="list" aria-label="Trust signals">
              {copy.hero.trustStrip.map((item) => (
                <div key={item} className="trust-strip__item" role="listitem">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </motion.section>

        <motion.section
          id="problem"
          className="section"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.25 }}
          transition={{ duration: 0.65, ease: "easeOut" }}
        >
          <div className="section-shell section-copy section-copy--single">
            <p className="section-kicker">01</p>
            <h2>{copy.problem.title}</h2>
            <p>{copy.problem.body}</p>
            <p className="section-emphasis">{copy.problem.closing}</p>
          </div>
        </motion.section>

        <motion.section
          id="solutions"
          className="section"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.65, ease: "easeOut" }}
        >
          <div className="section-shell">
            <div className="section-copy">
              <p className="section-kicker">02</p>
              <h2>{copy.solution.title}</h2>
              <p className="section-emphasis">{copy.solution.support}</p>
            </div>
            <div className="steps-grid">
              {copy.solution.steps.map((step, index) => (
                <article key={step.title} className="content-card content-card--step">
                  <span className="content-card__index">0{index + 1}</span>
                  <h3>{step.title}</h3>
                  <p>{step.body}</p>
                </article>
              ))}
            </div>
          </div>
        </motion.section>

        <motion.section
          className="section"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.65, ease: "easeOut" }}
        >
          <div className="section-shell">
            <div className="section-copy">
              <p className="section-kicker">03</p>
              <h2>{copy.benefits.title}</h2>
            </div>
            <div className="benefits-grid">
              {copy.benefits.cards.map((card) => (
                <article key={card.title} className="content-card">
                  <p className="content-card__eyebrow">{card.eyebrow}</p>
                  <h3>{card.title}</h3>
                  <p>{card.body}</p>
                </article>
              ))}
            </div>
            <p className="section-footnote">{copy.benefits.closing}</p>
          </div>
        </motion.section>

        <motion.section
          id="technology"
          className="section"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.65, ease: "easeOut" }}
        >
          <div className="section-shell technology-grid">
            <div className="section-copy">
              <p className="section-kicker">04</p>
              <h2>{copy.technology.title}</h2>
              <p>{copy.technology.body}</p>
            </div>

            <div className="technology-panel">
              <div className="technology-panel__header">
                <span className="technology-panel__eyebrow">Digital Fit Engine</span>
                <p>{copy.technology.pauLabel}</p>
              </div>
              <div className="technology-modules">
                {copy.technology.modules.map((module) => (
                  <div key={module} className="technology-module">
                    <span className="technology-module__dot" aria-hidden="true" />
                    <span>{module}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.section>

        <motion.section
          id="pilots"
          className="section"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.65, ease: "easeOut" }}
        >
          <div className="section-shell">
            <div className="section-copy">
              <p className="section-kicker">05</p>
              <h2>{copy.trust.title}</h2>
              <p>{copy.trust.body}</p>
            </div>

            <div className="metrics-grid">
              {copy.trust.metrics.map((metric, index) => (
                <article key={metric.label} className="metric-card">
                  <p className="metric-card__value">
                    <MetricCounter locale={locale} index={index} fallback={metric.value} />
                  </p>
                  <p className="metric-card__label">{metric.label}</p>
                </article>
              ))}
            </div>

            <p className="section-footnote">{copy.trust.note}</p>

            <div className="pilot-preview">
              <div className="pilot-preview__intro">
                <p className="section-kicker">{copy.nav.pilots}</p>
                <h3>Digital Fit Engine</h3>
                <p>{copy.technology.pauLabel}</p>
                <button type="button" className="button button--secondary" onClick={handlePilotLaunch}>
                  {copy.nav.pilots}
                </button>
              </div>

              <div className="mirror-shell" data-active={pilotPreviewOpen ? "true" : undefined}>
                <div className="mirror-frame">
                  {pilotPreviewOpen ? (
                    <OfrendaOverlay
                      locale={locale}
                      elasticLabel={copy.technology.modules[2]}
                      julesLane={copy.hero.trustStrip[0]}
                      headerExtra={<p className="pilot-preview__tag">{copy.technology.pauLabel}</p>}
                      onOfrenda={(action) => {
                        void handlePilotAction(action);
                      }}
                    />
                  ) : (
                    <div className="pilot-preview__placeholder">
                      <p>TRYONYOU</p>
                      <span>{copy.technology.pauLabel}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        <motion.section
          id="about"
          className="section"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.65, ease: "easeOut" }}
        >
          <div className="section-shell cta-grid">
            <div className="section-copy">
              <p className="section-kicker">06</p>
              <h2>{copy.finalCta.title}</h2>
              <div className="hero-actions">
                <a className="button button--primary" href="#demo">
                  {copy.finalCta.cta}
                </a>
              </div>
              <p className="section-footnote section-footnote--left">{copy.finalCta.microcopy}</p>
            </div>

            <aside className="about-card">
              <p className="content-card__eyebrow">TRYONYOU</p>
              <h3>Digital Fit Engine</h3>
              <p>{copy.technology.pauLabel}</p>
              <ul className="module-list module-list--stacked">
                {copy.technology.modules.map((module) => (
                  <li key={module}>{module}</li>
                ))}
              </ul>
            </aside>
          </div>
        </motion.section>

        <motion.section
          id="demo"
          className="section section--demo"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.65, ease: "easeOut" }}
        >
          <div className="section-shell demo-grid">
            <div className="section-copy">
              <p className="section-kicker">07</p>
              <h2>{copy.demoForm.title}</h2>
              <p>{copy.demoForm.support}</p>
            </div>

            <form className="demo-form" onSubmit={handleSubmit}>
              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.fullName}</span>
                <input
                  type="text"
                  value={formState.fullName}
                  onChange={(event) => updateField("fullName", event.target.value)}
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.corporateEmail}</span>
                <input
                  type="email"
                  value={formState.corporateEmail}
                  onChange={(event) => updateField("corporateEmail", event.target.value)}
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.company}</span>
                <input
                  type="text"
                  value={formState.company}
                  onChange={(event) => updateField("company", event.target.value)}
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.role}</span>
                <input
                  type="text"
                  value={formState.role}
                  onChange={(event) => updateField("role", event.target.value)}
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.businessType}</span>
                <select
                  value={formState.businessType}
                  onChange={(event) => updateField("businessType", event.target.value)}
                  required
                >
                  <option value="" disabled>
                    {copy.demoForm.fieldLabels.businessType}
                  </option>
                  {copy.demoForm.businessTypeOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.primaryMarket}</span>
                <input
                  type="text"
                  value={formState.primaryMarket}
                  onChange={(event) => updateField("primaryMarket", event.target.value)}
                  required
                />
              </label>

              <label className="form-field form-field--full">
                <span>{copy.demoForm.fieldLabels.challenge}</span>
                <textarea
                  rows={4}
                  value={formState.challenge}
                  onChange={(event) => updateField("challenge", event.target.value)}
                  required
                />
              </label>

              <label className="form-field">
                <span>
                  {copy.demoForm.fieldLabels.volume}
                  <em>{copy.demoForm.optionalLabel}</em>
                </span>
                <input
                  type="text"
                  value={formState.volume}
                  onChange={(event) => updateField("volume", event.target.value)}
                />
              </label>

              <label className="form-field">
                <span>
                  {copy.demoForm.fieldLabels.horizon}
                  <em>{copy.demoForm.optionalLabel}</em>
                </span>
                <input
                  type="text"
                  value={formState.horizon}
                  onChange={(event) => updateField("horizon", event.target.value)}
                />
              </label>

              <label className="consent-field form-field--full">
                <input
                  type="checkbox"
                  checked={formState.consent}
                  onChange={(event) => updateField("consent", event.target.checked)}
                  required
                />
                <span>
                  {copy.demoForm.fieldLabels.consent}
                  <small>{copy.demoForm.consentHint}</small>
                </span>
              </label>

              <div className="form-actions form-field--full">
                <button type="submit" className="button button--primary" disabled={submitState === "submitting"}>
                  {submitState === "submitting" ? copy.demoForm.submitting : copy.demoForm.submit}
                </button>
              </div>

              <AnimatePresence mode="wait">
                {submitState === "success" ? (
                  <motion.div
                    key="success"
                    className="form-feedback form-feedback--success form-field--full"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                  >
                    <strong>{copy.demoForm.successTitle}</strong>
                    <span>{copy.demoForm.successBody}</span>
                  </motion.div>
                ) : null}
                {submitState === "error" ? (
                  <motion.div
                    key="error"
                    className="form-feedback form-feedback--error form-field--full"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                  >
                    <strong>{copy.demoForm.error}</strong>
                    <span>{copy.demoForm.retry}</span>
                  </motion.div>
                ) : null}
              </AnimatePresence>
            </form>
          </div>
        </motion.section>
      </main>

      <footer id="legal" className="site-footer">
        <div className="section-shell site-footer__inner">
          <p>{copy.footer.companyLine}</p>
          <div className="site-footer__links">
            <a href="#legal">{copy.footer.privacy}</a>
            <a href="#legal">{copy.footer.biometricData}</a>
            <a href="#legal">{copy.footer.terms}</a>
            <a href="#legal">{copy.footer.cookies}</a>
            <a href="#legal">{copy.footer.security}</a>
          </div>
        </div>
      </footer>

      <PauFloatingGuide locale={locale} />
    </div>
  );
}

export default App;
