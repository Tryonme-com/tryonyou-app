import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import RealTimeAvatar from "./components/RealTimeAvatar";
import { ORO_DIVINEO, SOVEREIGN_FIT_LABEL } from "./divineo/divineoV11Config";

// Lazy-load Balmain module for optimal INP
const DressMeInBalmain = lazy(() => import("./components/DressMeInBalmain"));
import { getDivineoCheckoutUrl } from "./divineo/envBootstrap";
import {
  initFirebaseApplet,
  initFirebaseAnalytics,
  initFirebaseAppCheckIfConfigured,
} from "./lib/firebaseApplet";
import { trackCoreEvent } from "./lib/coreEngineClient";
import { fetchJulesHealth, postMirrorSnap } from "./lib/julesClient";
import "./index.css";
import "./App.css";

/** Nodos parisinos autorizados para P.A.U. (Lafayette / Marais). */
const PAU_POSTAL_NODES = new Set(["75009", "75004"]);

/** Estado operativo bunker / preview (narrativa V10). */
const OPERATIONAL_STATE_DIAMANTE = "DIAMANTE" as const;

function setWindowOperationalStateDiamante(): void {
  const w = window as Window & { __TRYONYOU_OPERATIONAL_STATE__?: string };
  w.__TRYONYOU_OPERATIONAL_STATE__ = OPERATIONAL_STATE_DIAMANTE;
}

function readPostalFromWindowOrUrl(): string {
  const w = window as Window & { __TRYONYOU_POSTAL__?: string };
  const fromGlobal = (w.__TRYONYOU_POSTAL__ || "").trim();
  if (/^\d{5}$/.test(fromGlobal)) return fromGlobal;
  try {
    const u = new URL(window.location.href);
    const q = (u.searchParams.get("postal") || u.searchParams.get("cp") || "").trim();
    if (/^\d{5}$/.test(q)) return q;
  } catch {
    /* ignore */
  }
  return "";
}

/**
 * UserCheck truthy → autorizado (App Check debug + Pau).
 * Código postal 75009 o 75004 (URL, ?postal=, __TRYONYOU_POSTAL__) → Pau activo.
 */
function isPauAuthorized(): boolean {
  const w = window as Window & { UserCheck?: unknown };
  const uc = w.UserCheck;
  if (uc != null && uc !== false && uc !== "") return true;
  const postal = readPostalFromWindowOrUrl();
  return PAU_POSTAL_NODES.has(postal);
}

/** Primera pasada: UserCheck soberano para App Check + Pau (sin esperar efectos). */
function forceUserCheckIfPilotCold(): void {
  if (typeof window === "undefined") return;
  const win = window as Window & { UserCheck?: unknown };
  if (win.UserCheck != null && win.UserCheck !== false && win.UserCheck !== "") return;
  const postal = readPostalFromWindowOrUrl();
  const vite = (import.meta.env.VITE_DISTRICT as string | undefined)?.trim();
  const loc: "75009" | "75004" =
    vite === "75004" || postal === "75004"
      ? "75004"
      : vite === "75009" || postal === "75009"
        ? "75009"
        : "75009";
  win.UserCheck = {
    isAuthorized: true,
    role: "SOUVERAIN",
    nodos: ["75009", "75004"],
    contrato: "194.800€",
    location: loc,
    contract: loc === "75004" ? "MARAIS_88K" : "LAFAYETTE_109K",
    source: "pau_v10_forced_pilot",
    operationalState: OPERATIONAL_STATE_DIAMANTE,
    pilotVenue: loc === "75004" ? "BHV_MARAIS" : "GALERIES_LAFAYETTE",
  };
  setWindowOperationalStateDiamante();
}

/** Lafayette 75009 vs Marais 75004 (VITE_DISTRICT, UserCheck.location, ?postal=, __TRYONYOU_POSTAL__). */
function resolveActiveDistrict(): "75009" | "75004" | "" {
  const vite = (import.meta.env.VITE_DISTRICT as string | undefined)?.trim();
  if (vite === "75009" || vite === "75004") return vite;
  const w = window as Window & { UserCheck?: unknown };
  const uc = w.UserCheck;
  if (uc && typeof uc === "object" && uc !== null) {
    const loc = String((uc as { location?: string }).location ?? "").trim();
    if (loc === "75009" || loc === "75004") return loc;
  }
  const postal = readPostalFromWindowOrUrl();
  if (postal === "75009" || postal === "75004") return postal;
  return "";
}

function elasticLabelToVerdict(label: string): string {
  if (label.includes("Préférence drapé")) return "drape_bias";
  if (label.includes("Préférence tenue")) return "tension_bias";
  return "aligned";
}

type BunkerSyncResult =
  | { ok: true; data: unknown }
  | { ok: false; error: unknown };

async function syncLeadsToBunker(
  payload: Record<string, unknown>,
): Promise<BunkerSyncResult> {
  try {
    const response = await fetch("/api/vetos_core_inference", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...payload,
        system: "BunkerV10_Santuario",
      }),
    });

    const data: Record<string, unknown> = await response.json().catch(() => ({}));

    if (!response.ok) {
      return { ok: false, error: data };
    }

    if (data.status !== "success" || data.leads_synced !== true) {
      return { ok: false, error: data };
    }

    console.log("✅ Sistema Sincronizado:", data);
    return { ok: true, data };
  } catch (error) {
    console.error("❌ Error Crítico Bunker:", error);
    return { ok: false, error };
  }
}

/** Umbral Bpifrance / Mesa: explícito en payload (el API no asume 7500 por defecto). */
const OFRENDA_REVENUE_VALIDATION_EUR = 7500;

async function postLead(intent: OfrendaKey): Promise<void> {
  const payload = {
    intent,
    source: "ofrenda_v10",
    protocol: "zero_size",
    revenue_validation: OFRENDA_REVENUE_VALIDATION_EUR,
  };
  const bunker = await syncLeadsToBunker(payload);
  if (!bunker.ok) {
    console.warn("Bunker sync no completada; no se envía el lead a /api/v1/leads.", bunker.error);
    return;
  }
  try {
    const r = await fetch("/api/v1/leads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!r.ok) return;
    void (await r.json());
  } catch {
    /* hors ligne */
  }
}

async function postBetaWaitlist(): Promise<void> {
  const email = window.prompt("Email (opcional) para la lista beta:", "") ?? "";
  const payload = {
    email: email.trim() || undefined,
    source: "app_v10",
    user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "",
    ts: new Date().toISOString(),
  };
  try {
    const r = await fetch("/api/waitlist_beta", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const j = (await r.json().catch(() => ({}))) as {
      waitlist_persisted?: boolean;
      make_ok?: boolean;
    };
    if (!r.ok) {
      window.alert("Lista beta: error de API (revisa consola).");
      return;
    }
    window.alert(
      j.waitlist_persisted
        ? "Inscrito — Make + waitlist (leads_empire/waitlist.json o /tmp en Vercel)."
        : `Webhook Make: ${j.make_ok ? "ok" : "no configurado / fallo"}. Persistencia limitada en serverless.`,
    );
  } catch {
    window.alert("Sin conexión al bunker API.");
  }
}

async function postPerfectCheckout(fabricSensation: string): Promise<void> {
  try {
    const r = await fetch("/api/v1/checkout/perfect-selection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        fabric_sensation: fabricSensation,
        protocol: "zero_size",
        shopping_flow: "non_stop_card",
        anti_accumulation: true,
        single_size_certitude: true,
      }),
    });
    if (!r.ok) return;
    const j = (await r.json()) as {
      emotional_seal?: string;
      checkout_primary_url?: string;
      checkout_shopify_url?: string;
      checkout_amazon_url?: string;
    };
    if (j.emotional_seal) {
      window.alert(j.emotional_seal);
    }
    const primary = j.checkout_primary_url?.trim();
    const shop = j.checkout_shopify_url?.trim();
    const amz = j.checkout_amazon_url?.trim();
    const url = primary || shop || amz;
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    } else if (!j.emotional_seal) {
      window.alert(
        "Parcours enregistré — les ponts marchands seront actifs dès configuration serveur (Zero-Size).",
      );
    }
  } catch {
    /* silencieux */
  }
}

export default function App() {
  const pauSovereignBoot = useRef(false);
  if (!pauSovereignBoot.current) {
    pauSovereignBoot.current = true;
    forceUserCheckIfPilotCold();
  }

  const [elasticLabel, setElasticLabel] = useState("—");
  const [julesLane, setJulesLane] = useState<string>("Orchestration Jules…");
  const [emailHero, setEmailHero] = useState<string>("");
  const [mirrorPoweredOn, setMirrorPoweredOn] = useState(true);
  const [showBalmain, setShowBalmain] = useState(false);

  /** Re-render al cambiar UserCheck en consola / initPauAlpha; tick ligero. */
  const [pauDistrictTick, setPauDistrictTick] = useState(0);

  /** window.UserCheck truthy, o nodo postal 75009 / 75004 (Lafayette / Marais) → Pau activo. */
  const pauStarted = isPauAuthorized();

  useEffect(() => {
    const id = window.setInterval(() => setPauDistrictTick((n) => n + 1), 900);
    return () => clearInterval(id);
  }, []);
  useEffect(() => {
    const w = window as Window & {
      initPauAlpha?: () => void;
      launchMarais?: () => void;
    };
    const bumpPau = () => {
      setPauDistrictTick((n) => n + 1);
      const v = document.querySelector<HTMLVideoElement>(".app-pau video");
      void v?.play().catch(() => {});
    };
    w.initPauAlpha = bumpPau;
    w.launchMarais = () => {
      const win = window as Window & { UserCheck?: unknown };
      win.UserCheck = {
        isAuthorized: true,
        role: "SOUVERAIN",
        nodos: ["75009", "75004"],
        contrato: "194.800€",
        location: "75004",
        contract: "MARAIS_88K",
        operationalState: OPERATIONAL_STATE_DIAMANTE,
        pilotVenue: "BHV_MARAIS",
      };
      setWindowOperationalStateDiamante();
      bumpPau();
      console.log("✅ [BOOM]: Marais 75004 — pavo activo (contrat bunker 88k).");
    };
    bumpPau();
    window.requestAnimationFrame(() => bumpPau());
    return () => {
      delete w.initPauAlpha;
      delete w.launchMarais;
    };
  }, []);

  const activeDistrict = useMemo(() => resolveActiveDistrict(), [pauDistrictTick]);
  const isMaraisNode = activeDistrict === "75004";

  /** Galeries Lafayette (75009) y BHV Marais (75004): estado DIAMANTE + initPauAlpha(). */
  useEffect(() => {
    const d = resolveActiveDistrict();
    if (d !== "75009" && d !== "75004") return;
    setWindowOperationalStateDiamante();
    const w = window as Window & { initPauAlpha?: () => void };
    queueMicrotask(() => w.initPauAlpha?.());
  }, [activeDistrict, pauDistrictTick]);

  useEffect(() => {
    const app = initFirebaseApplet();
    if (!app) return;
    void initFirebaseAnalytics(app);
    void initFirebaseAppCheckIfConfigured(app);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const refreshHealth = async () => {
      const h = await fetchJulesHealth();
      if (cancelled) return;
      if (h?.ok) {
        setMirrorPoweredOn(h.mirror_enabled !== false);
        setJulesLane(
          `Jules · ${h.service ?? "omega"} · ${h.product_lane ?? "tryonyou_v10_omega"}`,
        );
        return;
      }
      setMirrorPoweredOn(true);
      setJulesLane(
        "Jules · prévisualisation locale (API Python non joignable sur ce port)",
      );
    };
    void refreshHealth();
    const intervalId = window.setInterval(() => {
      void refreshHealth();
    }, 15000);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, []);

  useEffect(() => {
    const onFit = (e: Event) => {
      const ce = e as CustomEvent<{ label?: string }>;
      const lab = ce.detail?.label;
      if (typeof lab === "string" && lab.length > 0) setElasticLabel(lab);
    };
    window.addEventListener("tryonyou:fit", onFit);
    return () => window.removeEventListener("tryonyou:fit", onFit);
  }, []);

  const onOfrenda = (key: OfrendaKey) => {
    if (!mirrorPoweredOn) {
      window.alert("Le miroir est momentanément suspendu par contrôle distant.");
      return;
    }
    if (key === "balmain") {
      void trackCoreEvent("balmain_dress_me_intent", {
        fabric_sensation: elasticLabel,
      });
      setShowBalmain(true);
      return;
    }
    if (key === "selection") {
      void trackCoreEvent("perfect_selection_intent", {
        fabric_sensation: elasticLabel,
      });
      void postPerfectCheckout(elasticLabel);
      return;
    }
    void postLead(key);
    const copy: Record<Exclude<OfrendaKey, "selection" | "balmain">, string> = {
      reserve: "QR cabine VIP — Lafayette, essai en courtoisie Divineo.",
      combo: "Lignes alternatives chargées — composition Zero-Size.",
      save: "Silhouette enregistrée sous protocole chiffré (aucune taille exposée).",
      share: "Partage généré — métadonnées d'ajustage neutralisées.",
    };
    window.alert(copy[key]);
  };

  const theSnap = () => {
    if (!pauStarted || !mirrorPoweredOn) return;
    void (async () => {
      await trackCoreEvent("silhouette_scan_intent", {
        fabric_sensation: elasticLabel,
        fabric_fit_verdict: elasticLabelToVerdict(elasticLabel),
      });
      const j = await postMirrorSnap(
        elasticLabel,
        elasticLabelToVerdict(elasticLabel),
      );
      const msg =
        j?.jules_msg ??
        "The Snap — votre ligne trouve son équilibre. Le drapé répond avec élégance, sans mesure visible.";
      window.alert(msg);
    })();
  };

  const onHeroSubmit = async () => {
    const email = emailHero.trim();
    const normalized =
      email.length > 0 ? email : window.prompt("Email para probarla hoy:", "") ?? "";
    const finalEmail = normalized.trim();
    if (!finalEmail) return;
    const payload = {
      email: finalEmail,
      source: "hero_above_the_fold",
      user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "",
      ts: new Date().toISOString(),
    };
    try {
      const r = await fetch("/api/waitlist_beta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = (await r.json().catch(() => ({}))) as {
        waitlist_persisted?: boolean;
        make_ok?: boolean;
      };
      if (!r.ok) {
        window.alert("No se ha podido registrar tu slot hoy. Prueba en unos minutos.");
        return;
      }
      window.alert(
        j.waitlist_persisted || j.make_ok
          ? "Slot reservado. Te contactaremos para probarla hoy."
          : "Hemos recibido tu solicitud. El bunker te confirmará en breve.",
      );
    } catch {
      window.alert("Sin conexión al bunker API.");
    }
  };

  return (
    <div className="app-root">
      <div className="app-stage" aria-hidden />

      {/* ─── Header ─────────────────────────────────────────────────────── */}
      <header className="app-header">
        <span className="app-logo">TryOnYou</span>
        <nav className="app-header-nav">
          <a href="#espejo" className="app-header-link">Espejo</a>
          <a href="#tecnologia" className="app-header-link">Tecnología</a>
          <a
            href={getDivineoCheckoutUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="app-header-cta"
          >
            {SOVEREIGN_FIT_LABEL}
          </a>
        </nav>
      </header>

      <div className="app-ui">

        {/* ─── Hero ───────────────────────────────────────────────────────── */}
        <section className="app-hero" id="hero">
          <div>
            <p className="app-hero-eyebrow">Brevet PCT/EP2025/067317</p>
            <h1 className="app-hero-title">
              Sabrás si te queda bien,{" "}
              <em>antes de comprarlo.</em>
            </h1>
            <p className="app-hero-lede">
              Espejo digital en talla real. Sin probadores crueles, sin tallas que hieren.
              La certeza de verte como eres antes de pagar un solo euro.
            </p>
            <div className="app-hero-form">
              <input
                type="email"
                value={emailHero}
                onChange={(e) => setEmailHero(e.target.value)}
                placeholder="Tu email para probarla hoy"
                className="app-hero-input"
              />
              <button
                type="button"
                onClick={onHeroSubmit}
                className="app-hero-btn"
              >
                Reservar slot
              </button>
            </div>
            <p style={{ marginTop: 16, fontSize: 11, letterSpacing: "0.08em", color: "rgba(245,239,224,0.50)" }}>
              5 slots disponibles hoy · Acceso beta privado
            </p>
          </div>

          {/* Mirror preview right side */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
            {elasticLabel !== "—" && (
              <span className="app-elastic-label">{elasticLabel}</span>
            )}
            <motion.div
              className="app-pau-row"
              style={{ padding: 0, margin: 0 }}
              animate={{
                boxShadow: [
                  `0 0 0 1px ${ORO_DIVINEO}33`,
                  `0 0 28px ${ORO_DIVINEO}55`,
                  `0 0 0 1px ${ORO_DIVINEO}33`,
                ],
              }}
              transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
            >
              <button
                type="button"
                id="espejo"
                className={
                  isMaraisNode && pauStarted ? "app-pau app-pau--marais" : "app-pau app-pau--lafayette"
                }
                disabled={!pauStarted || !mirrorPoweredOn}
                onClick={theSnap}
                title={
                  !mirrorPoweredOn
                    ? "P.A.U. — desactivado por kill-switch remoto"
                    : pauStarted
                      ? isMaraisNode
                        ? "P.A.U. — Marais 75004 (BHV) · contrat bunker 88k"
                        : activeDistrict === "75009"
                          ? "P.A.U. — Lafayette 75009"
                          : "P.A.U. — Lafayette / Marais (UserCheck)"
                      : "P.A.U. — requiere nodo 75009, 75004 o window.UserCheck"
                }
                aria-label="P.A.U. — snap et orchestration Jules"
                style={{
                  opacity: pauStarted && mirrorPoweredOn ? 1 : 0.55,
                  cursor: pauStarted && mirrorPoweredOn ? "pointer" : "not-allowed",
                }}
              >
                <RealTimeAvatar
                  variant={isMaraisNode ? "marais" : "lafayette"}
                  disabled={!pauStarted || !mirrorPoweredOn}
                  videoId={isMaraisNode ? "marais-v10-omega" : "pau-lafayette-v10"}
                />
              </button>
            </motion.div>
          </div>
        </section>

        {/* ─── Stats Strip ────────────────────────────────────────────────── */}
        <div className="app-stats">
          <div className="app-stat">
            <div className="app-stat-value">85%</div>
            <div className="app-stat-label">Reducción de devoluciones</div>
          </div>
          <div className="app-stat">
            <div className="app-stat-value">0.3s</div>
            <div className="app-stat-label">Tiempo de ajuste biométrico</div>
          </div>
          <div className="app-stat">
            <div className="app-stat-value">PCT</div>
            <div className="app-stat-label">Patente internacional EP2025</div>
          </div>
        </div>

        {/* ─── Ofrenda / Actions ──────────────────────────────────────────── */}
        <section className="app-section" id="tecnologia">
          <p className="app-section-eyebrow">Protocolo Zero-Size</p>
          <h2 className="app-section-title">
            La <em>talla perfecta</em>, sin tallas.
          </h2>
          <p style={{ fontSize: 15, lineHeight: 1.75, color: "rgba(245,239,224,0.75)", maxWidth: "52ch", marginBottom: 8 }}>
            El motor biométrico de TRYONYOU elimina el concepto de talla.
            Tu silueta real, proyectada sobre cualquier prenda, en tiempo real.
          </p>
          <OfrendaOverlay
            elasticLabel={elasticLabel}
            julesLane={julesLane}
            onOfrenda={onOfrenda}
            headerExtra={
              <button
                type="button"
                onClick={() => void postBetaWaitlist()}
                className="app-ofrenda-btn"
                style={{ marginTop: 16 }}
              >
                Únete a la beta privada
              </button>
            }
          />
        </section>

        {/* ─── Hairline ───────────────────────────────────────────────────── */}
        <div className="app-hairline" />

        {/* ─── Footer ─────────────────────────────────────────────────────── */}
        <footer className="app-footer">
          <div>
            <div className="app-footer-logo">TryOnYou</div>
            <p className="app-footer-tagline">
              El probador virtual de alta precisión para maisons de moda.
              Brevet PCT/EP2025/067317 · Protocolo Zero-Size.
            </p>
          </div>
          <div className="app-footer-meta">
            <div>tryonyou.pro</div>
            <div style={{ marginTop: 4 }}>
              <a
                href={getDivineoCheckoutUrl()}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#C9A84C", textDecoration: "none" }}
              >
                {SOVEREIGN_FIT_LABEL} →
              </a>
            </div>
            <div style={{ marginTop: 4, opacity: 0.55 }}>© 2025 LVT-ENG</div>
          </div>
        </footer>

      </div>

      {/* ═══════════════════════════════════════════════════════════════════
          DRESS ME IN BALMAIN — Physics-Driven Virtual Try-On Module
          ═══════════════════════════════════════════════════════════════════ */}
      <AnimatePresence>
        {showBalmain && (
          <motion.div
            key="balmain-overlay"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96, filter: "blur(8px)" }}
            transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 9999,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: "rgba(10, 8, 6, 0.92)",
              backdropFilter: "blur(16px)",
              padding: 20,
            }}
          >
            <Suspense
              fallback={
                <div style={{ color: "#D4AF37", letterSpacing: 4, fontSize: 12, textTransform: "uppercase" }}>
                  Loading Balmain Physics Engine...
                </div>
              }
            >
              <DressMeInBalmain onClose={() => setShowBalmain(false)} />
            </Suspense>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
