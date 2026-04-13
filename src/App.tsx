import {
  type ChangeEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { motion } from "framer-motion";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import { PreScanHook } from "./components/PreScanHook";
import { ORO_DIVINEO, SOVEREIGN_FIT_LABEL } from "./divineo/divineoV11Config";
import { getDivineoCheckoutUrl } from "./divineo/envBootstrap";
import {
  initFirebaseApplet,
  initFirebaseAnalytics,
  initFirebaseAppCheckIfConfigured,
} from "./lib/firebaseApplet";
import {
  getInaugurationStripeCheckoutUrl,
  getInaugurationStripeEnvUrl,
  getLafayetteStripeCheckoutUrl,
  openInaugurationStripeLiquidity,
} from "./lib/lafayetteCheckout";
import {
  pauInaugurationCompliment,
  withPauSeal,
} from "./lib/pauVoice";
import { fetchJulesHealth, postMirrorSnap } from "./lib/julesClient";
import { mirrorDigitalMiddleware } from "./lib/mirrorDigitalMiddleware";
import {
  type AppLocale,
  SALES_COPY,
  type SalesCopy,
  SUPPORTED_LOCALES,
  formatEurAmount,
} from "./locales/salesCopy";
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
  if (typeof uc === "object" && uc !== null) return true;
  if (uc === true) return true;
  const postal = readPostalFromWindowOrUrl();
  return PAU_POSTAL_NODES.has(postal);
}

function userCheckPilotObjectComplete(uc: unknown): boolean {
  if (typeof uc !== "object" || uc === null) return false;
  const nodos = (uc as { nodos?: unknown }).nodos;
  return Array.isArray(nodos) && nodos.length > 0;
}

/** Primera pasada: UserCheck soberano para App Check + Pau (sin esperar efectos). */
function forceUserCheckIfPilotCold(): void {
  if (typeof window === "undefined") return;
  const win = window as Window & { UserCheck?: unknown };
  if (userCheckPilotObjectComplete(win.UserCheck)) return;
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

    return { ok: true, data };
  } catch (error) {
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

async function postBetaWaitlist(copy: SalesCopy): Promise<void> {
  const email = window.prompt(copy.betaPromptEmail, "") ?? "";
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
      window.alert(copy.betaApiError);
      return;
    }
    const status = j.make_ok ? copy.betaWebhookStatusOk : copy.betaWebhookStatusFail;
    const webhookMsg = copy.betaWebhookStatusTemplate.replace("{{status}}", status);
    window.alert(
      withPauSeal(
        j.waitlist_persisted
          ? copy.betaWaitlistStored
          : webhookMsg,
      ),
    );
  } catch {
    window.alert(copy.bunkerOffline);
  }
}

async function postPerfectCheckout(fabricSensation: string, copy: SalesCopy): Promise<void> {
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
      window.alert(withPauSeal(String(j.emotional_seal)));
    }
    const primary = j.checkout_primary_url?.trim();
    const shop = j.checkout_shopify_url?.trim();
    const amz = j.checkout_amazon_url?.trim();
    const url = primary || shop || amz;
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    } else if (!j.emotional_seal) {
      window.alert(withPauSeal(copy.perfectSelectionFallback));
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
  const [locale, setLocale] = useState<AppLocale>("fr");
  const [julesLane, setJulesLane] = useState<string>(
    "PAU · Orchestration Jules…",
  );
  const [emailHero, setEmailHero] = useState<string>("");
  const [pauInaugurationWhisper, setPauInaugurationWhisper] = useState("");

  /** Pre-scan hook — shown once per session until dismissed or auto-timeout. */
  const [preScanVisible, setPreScanVisible] = useState(
    () => sessionStorage.getItem("tryonyou_prescan_done") !== "1",
  );

  /** Re-render al cambiar UserCheck en consola / initPauAlpha; tick ligero. */
  const [pauDistrictTick, setPauDistrictTick] = useState(0);

  /** window.UserCheck truthy, o nodo postal 75009 / 75004 (Lafayette / Marais) → Pau activo. */
  const pauStarted = isPauAuthorized();

  useEffect(() => {
    const id = window.setInterval(
      () => setPauDistrictTick((n: number) => n + 1),
      900,
    );
    return () => clearInterval(id);
  }, []);
  useEffect(() => {
    const w = window as Window & {
      initPauAlpha?: () => void;
      launchMarais?: () => void;
    };
    const bumpPau = () => {
      setPauDistrictTick((n: number) => n + 1);
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
  const copy = SALES_COPY[locale];

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
    void (async () => {
      const h = await fetchJulesHealth();
      if (cancelled) return;
      if (h?.ok) {
        setJulesLane(
          `PAU · Jules · ${h.service ?? "omega"} · ${h.product_lane ?? "tryonyou_v10_omega"} — orchestration avec âme`,
        );
      } else {
        setJulesLane(
          "PAU · Jules · preview locale — l’API chuchote encore; le divin arrive.",
        );
      }
    })();
    return () => {
      cancelled = true;
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
    if (key === "selection") {
      void postPerfectCheckout(elasticLabel, copy);
      return;
    }
    if (key === "balmain") {
      mirrorDigitalMiddleware.onBalmainClick(elasticLabel);
    }
    if (key === "reserve") {
      mirrorDigitalMiddleware.onReserveFittingClick(elasticLabel);
    }
    void postLead(key);
    const ofrendaCopy: Record<Exclude<OfrendaKey, "selection">, string> = {
      balmain: copy.ofrendaBalmain,
      reserve: copy.ofrendaReserve,
      combo: copy.ofrendaCombo,
      save: copy.ofrendaSave,
      share: copy.ofrendaShare,
    };
    window.alert(withPauSeal(ofrendaCopy[key]));
  };

  const theSnap = () => {
    if (!pauStarted) return;
    void (async () => {
      const j = await postMirrorSnap(
        elasticLabel,
        elasticLabelToVerdict(elasticLabel),
      );
      const msg =
        j?.jules_msg ??
        "The Snap — votre ligne trouve son équilibre. Le drapé répond avec élégance, sans mesure visible.";
      window.alert(withPauSeal(msg));
    })();
  };

  const onHeroSubmit = async () => {
    const email = emailHero.trim();
    const normalized =
      email.length > 0 ? email : window.prompt(copy.heroEmailPrompt, "") ?? "";
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
        window.alert(copy.heroSlotError);
        return;
      }
      window.alert(
        withPauSeal(
          j.waitlist_persisted || j.make_ok
            ? copy.heroSlotReserved
            : copy.heroSlotReceived,
        ),
      );
    } catch {
      window.alert(copy.bunkerOffline);
    }
  };

  const onLafayetteStripeCharge = () => {
    const url = getLafayetteStripeCheckoutUrl();
    if (!url) {
      window.alert(copy.lafayetteMissingCheckout);
      return;
    }
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const onInaugurationStripeCharge = () => {
    const url =
      getInaugurationStripeEnvUrl() || getInaugurationStripeCheckoutUrl();
    if (!url) {
      window.alert(copy.inaugurationMissingCheckout);
      return;
    }
    // Prioridad env inaugural; sin alert posterior que bloquee el flujo ni validación Shopify/Firebase.
    openInaugurationStripeLiquidity();
  };

  const BRANDS_MAESTROS = ["BALMAIN", "DIOR", "PRADA", "CHANEL", "YSL"] as const;

  return (
    <div
      className="app-root"
      style={{
        background: "linear-gradient(165deg, #0c0d10 0%, #141619 40%, #1a1b20 70%, #0c0d10 100%)",
        color: "#f5efe6",
      }}
    >
      <div className="app-stage" aria-hidden />

      <div className="app-ui">
        {/* ─── Hero Section ──────────────────────────────── */}
        <section
          className="hero-section"
          style={{
            padding: "40px 24px 20px",
            maxWidth: 960,
            margin: "0 auto",
          }}
        >
          <div className="hero-brand-row">
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div
                style={{
                  width: 56,
                  height: 56,
                  borderRadius: 14,
                  border: `1px solid ${ORO_DIVINEO}33`,
                  background: "rgba(212,175,55,0.06)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: "'Cinzel', Georgia, serif",
                  fontSize: 20,
                  fontWeight: 700,
                  color: ORO_DIVINEO,
                  letterSpacing: 2,
                  boxShadow: `0 4px 20px rgba(212,175,55,0.12)`,
                }}
              >
                TY
              </div>
              <div>
                <div style={{ fontFamily: "'Cinzel', Georgia, serif", fontSize: 16, letterSpacing: 6, color: "#f5efe6", fontWeight: 500 }}>
                  TRYONYOU
                </div>
                <div style={{ fontSize: 9, letterSpacing: 3, color: ORO_DIVINEO, marginTop: 2, textTransform: "uppercase" }}>
                  Maison Digitale
                </div>
              </div>
            </div>
            <div className="hero-locale-switch" role="group" aria-label={copy.localeLabel}>
              {SUPPORTED_LOCALES.map((loc) => (
                <button
                  key={loc}
                  type="button"
                  onClick={() => setLocale(loc)}
                  data-active={locale === loc ? "1" : undefined}
                >
                  {loc.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Brands row */}
          <div style={{
            display: "flex",
            justifyContent: "center",
            gap: 24,
            marginTop: 24,
            marginBottom: 28,
          }}>
            {BRANDS_MAESTROS.map((brand) => (
              <span
                key={brand}
                style={{
                  fontFamily: "'Cinzel', Georgia, serif",
                  fontSize: 10,
                  letterSpacing: 4,
                  color: `${ORO_DIVINEO}88`,
                  textTransform: "uppercase",
                  cursor: "default",
                }}
              >
                {brand}
              </span>
            ))}
          </div>

          <p
            style={{
              fontSize: 10,
              letterSpacing: 6,
              textTransform: "uppercase",
              color: ORO_DIVINEO,
              marginBottom: 12,
              fontWeight: 500,
            }}
          >
            {copy.badge}
          </p>
          <h1
            style={{
              fontFamily: "'Cinzel', Georgia, serif",
              fontSize: "clamp(28px, 4.5vw, 42px)",
              lineHeight: 1.2,
              margin: 0,
              color: "#f5efe6",
              fontWeight: 400,
              letterSpacing: 1,
            }}
          >
            {copy.heroTitle}
          </h1>
          <p
            style={{
              marginTop: 16,
              maxWidth: 540,
              fontSize: 14.5,
              lineHeight: 1.75,
              color: "#ece4d8",
              opacity: 0.85,
            }}
          >
            {copy.heroLead}
          </p>

          {/* Email capture */}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 10,
              marginTop: 24,
              alignItems: "center",
            }}
          >
            <input
              type="email"
              value={emailHero}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setEmailHero(e.target.value)
              }
              placeholder={copy.heroEmailPlaceholder}
              style={{
                flex: "1 1 220px",
                minWidth: 0,
                padding: "12px 18px",
                borderRadius: 999,
                border: `1px solid ${ORO_DIVINEO}33`,
                fontSize: 13,
                backgroundColor: "rgba(20,22,25,0.8)",
                color: "#f5efe6",
                outline: "none",
                backdropFilter: "blur(12px)",
              }}
            />
            <button
              type="button"
              onClick={onHeroSubmit}
              style={{
                flex: "0 0 auto",
                padding: "13px 28px",
                borderRadius: 999,
                border: "none",
                background: `linear-gradient(135deg, ${ORO_DIVINEO}, #c5a46d)`,
                color: "#0c0d10",
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: 3,
                textTransform: "uppercase",
                cursor: "pointer",
                boxShadow: `0 8px 28px rgba(212,175,55,0.25)`,
                fontFamily: "'Cinzel', Georgia, serif",
              }}
            >
              {copy.heroCta}
            </button>
          </div>
          <div className="hero-house-phrases">
            {copy.housePhrases.map((phrase) => (
              <p key={phrase}>« {phrase} »</p>
            ))}
          </div>

          {/* Inauguration CTA */}
          <div style={{ marginTop: 24 }}>
            <button
              type="button"
              onClick={onInaugurationStripeCharge}
              onMouseEnter={() => setPauInaugurationWhisper(pauInaugurationCompliment())}
              onFocus={() => setPauInaugurationWhisper(pauInaugurationCompliment())}
              title={
                pauInaugurationWhisper ||
                copy.inaugurationTitle
              }
              aria-label={copy.inaugurationAriaLabel}
              style={{
                width: "100%",
                maxWidth: 480,
                padding: "16px 24px",
                borderRadius: 12,
                border: `1px solid ${ORO_DIVINEO}`,
                background: "linear-gradient(145deg, #141619 0%, #1a1b20 50%, #0c0d10 100%)",
                color: ORO_DIVINEO,
                fontFamily: "'Cinzel', Georgia, serif",
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: 4,
                textTransform: "uppercase",
                cursor: "pointer",
                boxShadow: `0 8px 32px rgba(212,175,55,0.2), inset 0 1px 0 rgba(212,175,55,0.15)`,
                transition: "all 0.3s ease",
              }}
            >
              {copy.inaugurationCta}
            </button>
            {pauInaugurationWhisper ? (
              <p
                style={{
                  marginTop: 12,
                  maxWidth: 480,
                  fontSize: 13,
                  lineHeight: 1.6,
                  fontStyle: "italic",
                  color: `${ORO_DIVINEO}cc`,
                }}
              >
                PAU · {pauInaugurationWhisper}
              </p>
            ) : null}
          </div>

          {/* Lafayette CTA */}
          <div style={{ marginTop: 12 }}>
            <button
              type="button"
              onClick={onLafayetteStripeCharge}
              style={{
                width: "100%",
                maxWidth: 480,
                padding: "12px 20px",
                borderRadius: 10,
                border: `1px solid ${ORO_DIVINEO}22`,
                background: "rgba(212,175,55,0.06)",
                color: "#ece4d8",
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: 2.5,
                textTransform: "uppercase",
                cursor: "pointer",
                fontFamily: "'Cinzel', Georgia, serif",
                transition: "all 0.3s ease",
              }}
            >
              {copy.lafayetteCta}
            </button>
          </div>

          {/* Pricing grid */}
          <div className="hero-pricing-grid">
            <article>
              <h3>{copy.packStarterTitle}</h3>
              <p className="hero-price">{formatEurAmount(12500, locale)}</p>
              <p>{copy.packStarterBody}</p>
            </article>
            <article>
              <h3>{copy.packMaisonTitle}</h3>
              <p className="hero-price">{formatEurAmount(109900, locale)}</p>
              <p>{copy.packMaisonBody}</p>
            </article>
          </div>

          {/* Sales videos */}
          <div className="sales-video-row">
            <article>
              <h3>{copy.videoOneTitle}</h3>
              <video controls preload="metadata" playsInline>
                <source src="/videos/pau_sales_intro.mp4" type="video/mp4" />
              </video>
              <p>{copy.videoOneBody}</p>
            </article>
            <article>
              <h3>{copy.videoTwoTitle}</h3>
              <video controls preload="metadata" playsInline>
                <source src="/videos/pau_sales_close.mp4" type="video/mp4" />
              </video>
              <p>{copy.videoTwoBody}</p>
            </article>
          </div>

          {/* Checkout link */}
          <p
            style={{
              marginTop: 18,
              fontSize: 12,
              letterSpacing: 1.5,
              color: `${ORO_DIVINEO}99`,
            }}
          >
            <a
              href={getDivineoCheckoutUrl()}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: ORO_DIVINEO,
                fontWeight: 600,
                textDecoration: "none",
                borderBottom: `1px solid ${ORO_DIVINEO}66`,
                paddingBottom: 1,
              }}
            >
              {SOVEREIGN_FIT_LABEL}
            </a>
            <span style={{ opacity: 0.7 }}>{copy.checkoutHint}</span>
          </p>
        </section>

          {/* ─── Impact Section: The 0sizes Era ──────── */}
        <section
          style={{
            padding: "48px 20px",
            maxWidth: 960,
            margin: "0 auto",
            textAlign: "center",
          }}
        >
          <h2
            style={{
              fontSize: "clamp(22px, 3.5vw, 34px)",
              fontFamily: "'Cinzel', Georgia, serif",
              letterSpacing: 4,
              color: "#ece4d8",
              marginBottom: 8,
            }}
          >
            Le fin des tailles et des retours
          </h2>
          <p
            style={{
              fontSize: "clamp(16px, 2.5vw, 24px)",
              fontFamily: "'Cinzel', Georgia, serif",
              letterSpacing: 6,
              color: ORO_DIVINEO,
              marginBottom: 32,
              fontWeight: 700,
            }}
          >
            THE 0SIZES ERA
          </p>
          {/* Video Inauguration */}
          <div style={{ marginBottom: 32 }}>
            <video
              autoPlay
              loop
              muted
              playsInline
              style={{
                width: "100%",
                maxWidth: 800,
                borderRadius: 12,
                boxShadow: `0 12px 48px rgba(0,0,0,0.4)`,
              }}
            >
              <source src="/assets/videos/inauguration_theatre.mp4" type="video/mp4" />
            </video>
          </div>
          {/* Metrics Grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: 20,
              marginBottom: 32,
            }}
          >
            <div style={{ padding: 20, background: "rgba(212,175,55,0.08)", borderRadius: 12, border: `1px solid ${ORO_DIVINEO}22` }}>
              <p style={{ fontSize: 32, fontWeight: 700, color: ORO_DIVINEO, margin: 0 }}>-85%</p>
              <p style={{ fontSize: 12, letterSpacing: 2, color: "#ece4d8", marginTop: 6 }}>RETOURS ÉLIMINÉS</p>
            </div>
            <div style={{ padding: 20, background: "rgba(212,175,55,0.08)", borderRadius: 12, border: `1px solid ${ORO_DIVINEO}22` }}>
              <p style={{ fontSize: 32, fontWeight: 700, color: ORO_DIVINEO, margin: 0 }}>+25%</p>
              <p style={{ fontSize: 12, letterSpacing: 2, color: "#ece4d8", marginTop: 6 }}>CONVERSION VENTES</p>
            </div>
            <div style={{ padding: 20, background: "rgba(212,175,55,0.08)", borderRadius: 12, border: `1px solid ${ORO_DIVINEO}22` }}>
              <p style={{ fontSize: 32, fontWeight: 700, color: ORO_DIVINEO, margin: 0 }}>99.7%</p>
              <p style={{ fontSize: 12, letterSpacing: 2, color: "#ece4d8", marginTop: 6 }}>PRÉCISION BIOMÉTRIQUE</p>
            </div>
            <div style={{ padding: 20, background: "rgba(212,175,55,0.08)", borderRadius: 12, border: `1px solid ${ORO_DIVINEO}22` }}>
              <p style={{ fontSize: 32, fontWeight: 700, color: ORO_DIVINEO, margin: 0 }}>10K</p>
              <p style={{ fontSize: 12, letterSpacing: 2, color: "#ece4d8", marginTop: 6 }}>UTILISATEURS SIMULTANÉS</p>
            </div>
          </div>
          {/* Patent & Certification */}
          <div
            style={{
              padding: "24px 28px",
              background: "rgba(0,0,0,0.3)",
              borderRadius: 12,
              border: `1px solid ${ORO_DIVINEO}33`,
              marginBottom: 32,
            }}
          >
            <p style={{ fontSize: 11, letterSpacing: 3, color: ORO_DIVINEO, marginBottom: 8 }}>PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE</p>
            <p style={{ fontSize: 16, color: "#ece4d8", fontFamily: "'Cinzel', Georgia, serif" }}>Brevet International PCT/EP2025/067317</p>
            <p style={{ fontSize: 12, color: "#ece4d8aa", marginTop: 8 }}>8 Super-Claims · Valorisation 17M€ — 26M€ · The Snap™ · Génération Adaptative d'Avatars</p>
          </div>
          {/* Contract Info */}
          <div
            style={{
              padding: "20px 24px",
              background: "rgba(212,175,55,0.06)",
              borderRadius: 12,
              border: `1px solid ${ORO_DIVINEO}22`,
              textAlign: "left",
            }}
          >
            <p style={{ fontSize: 11, letterSpacing: 3, color: ORO_DIVINEO, marginBottom: 12 }}>CONTRAT DE LICENCE — GALERIES LAFAYETTE</p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <p style={{ fontSize: 10, color: "#ece4d8aa", margin: 0 }}>Setup Fee</p>
                <p style={{ fontSize: 18, color: "#ece4d8", fontWeight: 700, margin: "4px 0" }}>12 500 €</p>
              </div>
              <div>
                <p style={{ fontSize: 10, color: "#ece4d8aa", margin: 0 }}>Exclusivité Territoriale</p>
                <p style={{ fontSize: 18, color: "#ece4d8", fontWeight: 700, margin: "4px 0" }}>15 000 €</p>
              </div>
              <div>
                <p style={{ fontSize: 10, color: "#ece4d8aa", margin: 0 }}>Royalties sur Ventes</p>
                <p style={{ fontSize: 18, color: ORO_DIVINEO, fontWeight: 700, margin: "4px 0" }}>8%</p>
              </div>
              <div>
                <p style={{ fontSize: 10, color: "#ece4d8aa", margin: 0 }}>Total Immédiat</p>
                <p style={{ fontSize: 18, color: ORO_DIVINEO, fontWeight: 700, margin: "4px 0" }}>27 500 €</p>
              </div>
            </div>
          </div>
        </section>
        {/* ─── Ofrenda Overlay ──────────────────────────── */}
        <OfrendaOverlayay
          elasticLabel={elasticLabel}
          julesLane={julesLane}
          onOfrenda={onOfrenda}
          locale={locale}
          headerExtra={
            <button
              type="button"
              onClick={() => void postBetaWaitlist(copy)}
              style={{
                marginTop: 16,
                padding: "10px 22px",
                fontSize: 10,
                letterSpacing: 3,
                textTransform: "uppercase",
                color: ORO_DIVINEO,
                background: "rgba(212,175,55,0.08)",
                border: `1px solid ${ORO_DIVINEO}44`,
                borderRadius: 999,
                cursor: "pointer",
                fontFamily: "'Cinzel', Georgia, serif",
                transition: "all 0.3s ease",
              }}
            >
              {copy.betaCta}
            </button>
          }
        />

        {/* ─── P.A.U. Avatar ───────────────────────────── */}
        <motion.div
          className="app-pau-row"
          animate={{
            boxShadow: [
              `0 0 0 1px ${ORO_DIVINEO}22`,
              `0 0 32px ${ORO_DIVINEO}44`,
              `0 0 0 1px ${ORO_DIVINEO}22`,
            ],
          }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
        >
          <button
            type="button"
            className={
              isMaraisNode && pauStarted ? "app-pau app-pau--marais" : "app-pau app-pau--lafayette"
            }
            disabled={!pauStarted}
            onClick={theSnap}
            title={
              pauStarted
                ? isMaraisNode
                  ? "P.A.U. — Marais 75004 (BHV) · contrat bunker 88k"
                  : activeDistrict === "75009"
                    ? "P.A.U. — Lafayette 75009"
                    : "P.A.U. — Lafayette / Marais (UserCheck)"
                : "P.A.U. — requiere nodo 75009, 75004 o window.UserCheck"
            }
            aria-label="P.A.U. — snap et orchestration Jules"
            style={{
              opacity: pauStarted ? 1 : 0.55,
              cursor: pauStarted ? "pointer" : "not-allowed",
            }}
          >
            <video
              key={isMaraisNode ? "marais" : "lafayette"}
              id={isMaraisNode ? "marais-v10-omega" : "pau-lafayette-v10"}
              autoPlay
              loop
              muted
              playsInline
              preload="auto"
            >
              {isMaraisNode ? (
                <>
                  <source src="/assets/marais_pau_v10.mp4" type="video/mp4" />
                  <source src="/videos/pau_transparent.webm" type="video/webm" />
                  <source src="/videos/pau_transparent.mp4" type="video/mp4" />
                </>
              ) : (
                <>
                  <source src="/videos/pau_transparent.webm" type="video/webm" />
                  <source src="/videos/pau_transparent.mp4" type="video/mp4" />
                </>
              )}
            </video>
          </button>
        </motion.div>

        {/* ─── Footer ──────────────────────────────────── */}
        <div className="app-legal">
          SIRET 94361019600017 · PCT/EP2025/067317 · TRYONYOU V11 SOVEREIGN
        </div>
      </div>

      <PreScanHook
        visible={preScanVisible}
        onDismiss={() => {
          sessionStorage.setItem("tryonyou_prescan_done", "1");
          setPreScanVisible(false);
        }}
      />
    </div>
  );
}
