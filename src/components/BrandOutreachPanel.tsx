import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ORO_DIVINEO } from "../divineo/divineoV11Config";
import type { AppLocale } from "../locales/salesCopy";

type Brand = {
  brand: string;
  segment: string;
};

const SEGMENTS_ORDER = [
  "Haute Couture",
  "Luxury RTW",
  "Premium",
  "Contemporary",
  "Haute Joaillerie",
  "Fine Jewellery",
];

const COPY: Record<
  AppLocale,
  {
    section: string;
    title: string;
    subtitle: string;
    configured: string;
    notConfigured: string;
    brandCount: string;
    sendSingle: string;
    brandLabel: string;
    emailLabel: string;
    langLabel: string;
    send: string;
    sending: string;
    success: string;
    error: string;
    loading: string;
    logTitle: string;
    noLogs: string;
  }
> = {
  fr: {
    section: "09",
    title: "Outreach B2B",
    subtitle:
      "Propositions de pilote miroir digital aux marques. Envoi via Resend.",
    configured: "Resend configuré",
    notConfigured: "Resend non configuré",
    brandCount: "marques référencées",
    sendSingle: "Envoyer une proposition",
    brandLabel: "Marque",
    emailLabel: "Email du contact",
    langLabel: "Langue",
    send: "Envoyer",
    sending: "Envoi…",
    success: "Proposition envoyée",
    error: "Erreur d'envoi",
    loading: "Chargement…",
    logTitle: "Derniers envois",
    noLogs: "Aucun envoi enregistré",
  },
  en: {
    section: "09",
    title: "B2B Outreach",
    subtitle:
      "Digital mirror pilot proposals to brands. Powered by Resend.",
    configured: "Resend configured",
    notConfigured: "Resend not configured",
    brandCount: "brands referenced",
    sendSingle: "Send a proposal",
    brandLabel: "Brand",
    emailLabel: "Contact email",
    langLabel: "Language",
    send: "Send",
    sending: "Sending…",
    success: "Proposal sent",
    error: "Send error",
    loading: "Loading…",
    logTitle: "Recent sends",
    noLogs: "No sends recorded",
  },
  es: {
    section: "09",
    title: "Outreach B2B",
    subtitle:
      "Propuestas de piloto espejo digital a marcas. Envío vía Resend.",
    configured: "Resend configurado",
    notConfigured: "Resend no configurado",
    brandCount: "marcas referenciadas",
    sendSingle: "Enviar propuesta",
    brandLabel: "Marca",
    emailLabel: "Email del contacto",
    langLabel: "Idioma",
    send: "Enviar",
    sending: "Enviando…",
    success: "Propuesta enviada",
    error: "Error de envío",
    loading: "Cargando…",
    logTitle: "Últimos envíos",
    noLogs: "Sin envíos registrados",
  },
};

type Props = {
  locale: AppLocale;
};

export function BrandOutreachPanel({ locale }: Props) {
  const c = COPY[locale];
  const [brands, setBrands] = useState<Brand[]>([]);
  const [configured, setConfigured] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const [selectedBrand, setSelectedBrand] = useState("");
  const [email, setEmail] = useState("");
  const [lang, setLang] = useState<string>(locale);
  const [sending, setSending] = useState(false);
  const [feedback, setFeedback] = useState<{
    ok: boolean;
    msg: string;
  } | null>(null);

  const [logs, setLogs] = useState<
    { ts: string; brand: string; email: string; status: string }[]
  >([]);

  const fetchBrands = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/outreach/brands", {
        credentials: "same-origin",
      });
      if (res.ok) {
        const json = await res.json();
        setBrands(json.brands ?? []);
        setConfigured(!!json.configured);
        if (json.brands?.length) setSelectedBrand(json.brands[0].brand);
      }
    } catch {
      /* offline */
    }
    setLoaded(true);
  }, []);

  const fetchLogs = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/outreach/logs?limit=10", {
        credentials: "same-origin",
      });
      if (res.ok) {
        const json = await res.json();
        setLogs(json.logs ?? []);
      }
    } catch {
      /* offline */
    }
  }, []);

  useEffect(() => {
    void fetchBrands();
    void fetchLogs();
  }, [fetchBrands, fetchLogs]);

  const handleSend = async () => {
    if (!selectedBrand || !email) return;
    setSending(true);
    setFeedback(null);
    try {
      const matched = brands.find((b) => b.brand === selectedBrand);
      const res = await fetch("/api/v1/outreach/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({
          brand: selectedBrand,
          email,
          lang,
          segment: matched?.segment ?? "Luxury RTW",
        }),
      });
      const json = await res.json();
      setFeedback({
        ok: !!json.ok,
        msg: json.ok ? c.success : json.error ?? c.error,
      });
      if (json.ok) {
        setEmail("");
        void fetchLogs();
      }
    } catch {
      setFeedback({ ok: false, msg: c.error });
    }
    setSending(false);
  };

  if (!loaded) {
    return (
      <div className="orchestration-panel orchestration-panel--loading">
        <p>{c.loading}</p>
      </div>
    );
  }

  const grouped = SEGMENTS_ORDER.reduce<Record<string, Brand[]>>(
    (acc, seg) => {
      const items = brands.filter((b) => b.segment === seg);
      if (items.length) acc[seg] = items;
      return acc;
    },
    {},
  );

  return (
    <motion.div
      className="orchestration-panel"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.5 }}
    >
      <p className="section-kicker" style={{ color: ORO_DIVINEO }}>
        {c.section}
      </p>
      <h3 style={{ color: "#fff", margin: "0 0 4px" }}>{c.title}</h3>
      <p className="orchestration-panel__subtitle">{c.subtitle}</p>

      {/* Status bar */}
      <div className="orchestration-panel__grid" style={{ marginBottom: 16 }}>
        <div className="orchestration-panel__card">
          <span className="orchestration-panel__label">Resend</span>
          <span
            className="orchestration-panel__value"
            style={{ color: configured ? "#4ade80" : "#f87171" }}
          >
            {configured ? c.configured : c.notConfigured}
          </span>
        </div>
        <div className="orchestration-panel__card">
          <span className="orchestration-panel__label">{c.brandCount}</span>
          <span className="orchestration-panel__value">{brands.length}</span>
        </div>
      </div>

      {/* Brand segments */}
      <div style={{ marginBottom: 20 }}>
        {Object.entries(grouped).map(([seg, items]) => (
          <div key={seg} style={{ marginBottom: 10 }}>
            <span
              className="orchestration-panel__label"
              style={{ display: "block", marginBottom: 4 }}
            >
              {seg}
            </span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {items.map((b) => (
                <span
                  key={b.brand}
                  className="orchestration-panel__kpi-item"
                  style={{
                    cursor: "pointer",
                    borderColor:
                      selectedBrand === b.brand ? ORO_DIVINEO : undefined,
                    color:
                      selectedBrand === b.brand ? ORO_DIVINEO : undefined,
                  }}
                  onClick={() => setSelectedBrand(b.brand)}
                >
                  {b.brand}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Send form */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr auto auto",
          gap: 10,
          alignItems: "end",
          marginBottom: 16,
        }}
      >
        <label style={{ fontSize: 13, color: "#aaa" }}>
          {c.brandLabel}
          <select
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            style={{
              display: "block",
              width: "100%",
              marginTop: 4,
              padding: "8px 10px",
              background: "#1e2024",
              border: `1px solid ${ORO_DIVINEO}40`,
              borderRadius: 6,
              color: "#fff",
              fontSize: 14,
            }}
          >
            {brands.map((b) => (
              <option key={b.brand} value={b.brand}>
                {b.brand}
              </option>
            ))}
          </select>
        </label>

        <label style={{ fontSize: 13, color: "#aaa" }}>
          {c.emailLabel}
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="contact@brand.com"
            style={{
              display: "block",
              width: "100%",
              marginTop: 4,
              padding: "8px 10px",
              background: "#1e2024",
              border: `1px solid ${ORO_DIVINEO}40`,
              borderRadius: 6,
              color: "#fff",
              fontSize: 14,
            }}
          />
        </label>

        <label style={{ fontSize: 13, color: "#aaa" }}>
          {c.langLabel}
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value)}
            style={{
              display: "block",
              marginTop: 4,
              padding: "8px 10px",
              background: "#1e2024",
              border: `1px solid ${ORO_DIVINEO}40`,
              borderRadius: 6,
              color: "#fff",
              fontSize: 14,
            }}
          >
            <option value="fr">FR</option>
            <option value="en">EN</option>
            <option value="es">ES</option>
          </select>
        </label>

        <button
          onClick={handleSend}
          disabled={sending || !email || !selectedBrand}
          style={{
            alignSelf: "end",
            padding: "9px 20px",
            background: `linear-gradient(135deg, ${ORO_DIVINEO}, #b8962e)`,
            border: "none",
            borderRadius: 6,
            color: "#000",
            fontWeight: 700,
            fontSize: 14,
            cursor: sending ? "wait" : "pointer",
            opacity: sending || !email ? 0.5 : 1,
            letterSpacing: "0.04em",
            textTransform: "uppercase",
          }}
        >
          {sending ? c.sending : c.send}
        </button>
      </div>

      {feedback && (
        <p
          style={{
            fontSize: 13,
            color: feedback.ok ? "#4ade80" : "#f87171",
            marginBottom: 12,
          }}
        >
          {feedback.ok ? "✓ " : "✗ "}
          {feedback.msg}
        </p>
      )}

      {/* Recent logs */}
      {logs.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <span
            className="orchestration-panel__label"
            style={{ display: "block", marginBottom: 6 }}
          >
            {c.logTitle}
          </span>
          <ul
            style={{
              listStyle: "none",
              padding: 0,
              margin: 0,
              fontSize: 12,
              color: "#888",
            }}
          >
            {logs.map((l, i) => (
              <li
                key={`${l.ts}-${i}`}
                style={{
                  padding: "4px 0",
                  borderBottom: "1px solid #ffffff0a",
                }}
              >
                <span style={{ color: l.status === "sent" ? "#4ade80" : "#f87171" }}>
                  {l.status === "sent" ? "✓" : "✗"}
                </span>{" "}
                <strong style={{ color: "#ccc" }}>{l.brand}</strong> → {l.email}{" "}
                <span style={{ opacity: 0.5 }}>
                  {new Date(l.ts).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}
