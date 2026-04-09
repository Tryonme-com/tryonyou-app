import {
  type ChangeEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { motion } from "framer-motion";
import { MirrorSnap } from "./components/MirrorSnap";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
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
      withPauSeal(
        j.waitlist_persisted
          ? "Inscrito — Make + waitlist (leads_empire/waitlist.json o /tmp en Vercel)."
          : `Webhook Make: ${j.make_ok ? "ok" : "no configurado / fallo"}. Persistencia limitada en serverless.`,
      ),
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
      window.alert(withPauSeal(String(j.emotional_seal)));
    }
    const primary = j.checkout_primary_url?.trim();
    const shop = j.checkout_shopify_url?.trim();
    const amz = j.checkout_amazon_url?.trim();
    const url = primary || shop || amz;
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    } else if (!j.emotional_seal) {
      window.alert(
        withPauSeal(
          "Parcours enregistré — les ponts marchands seront actifs dès configuration serveur (Zero-Size).",
        ),
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
  const [julesLane, setJulesLane] = useState<string>(
    "PAU · Orchestration Jules…",
  );
  const [emailHero, setEmailHero] = useState<string>("");
  const [pauInaugurationWhisper, setPauInaugurationWhisper] = useState("");

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

  /**
   * Guard de soberanía UI:
   * si un widget externo inyecta calibración por números (cm/height),
   * la desactiva para priorizar calibración automática por punto de suelo.
   */
  useEffect(() => {
    const blockNumericCalibrator = () => {
      const suspicious = Array.from(
        document.querySelectorAll<HTMLInputElement>('input[type="number"], input[inputmode="decimal"]'),
      );
      for (const el of suspicious) {
        const text = ((el.placeholder || "") + " " + (el.getAttribute("aria-label") || "")).toLowerCase();
        if (text.includes("height") || text.includes("cm") || text.includes("calibr")) {
          const box = (el.closest("form") || el.parentElement) as HTMLElement | null;
          if (box) box.style.display = "none";
        }
      }
    };
    const obs = new MutationObserver(() => blockNumericCalibrator());
    obs.observe(document.body, { subtree: true, childList: true, attributes: true });
    blockNumericCalibrator();
    return () => obs.disconnect();
  }, []);

  const onOfrenda = (key: OfrendaKey) => {
    if (key === "selection") {
      void postPerfectCheckout(elasticLabel);
      return;
    }
    if (key === "balmain") {
      mirrorDigitalMiddleware.onBalmainClick(elasticLabel);
    }
    if (key === "reserve") {
      mirrorDigitalMiddleware.onReserveFittingClick(elasticLabel);
    }
    void postLead(key);
    const copy: Record<Exclude<OfrendaKey, "selection">, string> = {
      balmain: "Ligne Balmain — Espejo Digital notificado; poursuite sous protocole Zero-Size.",
      reserve: "QR cabine VIP — Lafayette, essai en courtoisie Divineo.",
      combo: "Lignes alternatives chargées — composition Zero-Size.",
      save: "Silhouette enregistrée sous protocole chiffré (aucune taille exposée).",
      share: "Partage généré — métadonnées d’ajustage neutralisées.",
    };
    window.alert(withPauSeal(copy[key]));
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
        withPauSeal(
          j.waitlist_persisted || j.make_ok
            ? "Slot reservado. Te contactaremos para probarla hoy."
            : "Hemos recibido tu solicitud. El bunker te confirmará en breve.",
        ),
      );
    } catch {
      window.alert("Sin conexión al bunker API.");
    }
  };

  const onLafayetteStripeCharge = () => {
    const url = getLafayetteStripeCheckoutUrl();
    if (!url) {
      window.alert(
        "Contrato Lafayette: define VITE_LAFAYETTE_STRIPE_CHECKOUT_URL (Stripe Payment Link LIVE) en Vercel o .env local.",
      );
      return;
    }
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const onInaugurationStripeCharge = () => {
    const url =
      getInaugurationStripeEnvUrl() || getInaugurationStripeCheckoutUrl();
    if (!url) {
      window.alert(
        "Liquidez: configura VITE_INAUGURATION_STRIPE_CHECKOUT_URL (Payment Link LIVE 12.500 €) en Vercel / .env.",
      );
      return;
    }
    // Prioridad env inaugural; sin alert posterior que bloquee el flujo ni validación Shopify/Firebase.
    openInaugurationStripeLiquidity();
  };

  return (
    <div
      className="app-root"
      style={{
        background: "linear-gradient(145deg, #F5F5DC 0%, #FFFFFF 38%, #D3B26A 100%)",
        color: "#111111",
      }}
    >
      <div className="app-stage" aria-hidden />

      <div className="app-ui">
        <section
          style={{
            padding: "32px 20px 12px",
            maxWidth: 960,
            margin: "0 auto",
          }}
        >
          <p
            style={{
              fontSize: 11,
              letterSpacing: 6,
              textTransform: "uppercase",
              color: "#6b5b3a",
              marginBottom: 10,
            }}
          >
            TRYONYOU · DIVINEO
          </p>
          <h1
            style={{
              fontSize: "clamp(26px, 4vw, 38px)",
              lineHeight: 1.15,
              margin: 0,
              color: "#26201A",
            }}
          >
            Sabrás si te queda bien, antes de comprarlo.
          </h1>
          <p
            style={{
              marginTop: 14,
              maxWidth: 520,
              fontSize: 14,
              lineHeight: 1.7,
              color: "#4a4034",
            }}
          >
            Espejo digital en talla real. Sin probadores crueles, sin tallas que hieren.
            Solo la certeza de verte como eres antes de pagar un solo euro.
          </p>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 10,
              marginTop: 18,
              alignItems: "center",
            }}
          >
            <input
              type="email"
              value={emailHero}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setEmailHero(e.target.value)
              }
              placeholder="Tu email para probarla hoy"
              style={{
                flex: "1 1 220px",
                minWidth: 0,
                padding: "10px 14px",
                borderRadius: 999,
                border: "1px solid rgba(0,0,0,0.18)",
                fontSize: 13,
                backgroundColor: "rgba(255,255,255,0.9)",
              }}
            />
            <button
              type="button"
              onClick={onHeroSubmit}
              style={{
                flex: "0 0 auto",
                padding: "11px 22px",
                borderRadius: 999,
                border: "none",
                backgroundColor: "#D3B26A",
                color: "#111111",
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: 2,
                textTransform: "uppercase",
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(0,0,0,0.12)",
              }}
            >
              Pruébatela YA (5 slots hoy)
            </button>
          </div>
          <div style={{ marginTop: 16 }}>
            <button
              type="button"
              onClick={onInaugurationStripeCharge}
              onMouseEnter={() => setPauInaugurationWhisper(pauInaugurationCompliment())}
              onFocus={() => setPauInaugurationWhisper(pauInaugurationCompliment())}
              title={
                pauInaugurationWhisper ||
                "PAU — inauguración soberana LIVE; tu visión merece este sello."
              }
              aria-label="PAU — PAGAR 12.500 euros inauguración LIVE (Stripe)"
              style={{
                width: "100%",
                maxWidth: 440,
                padding: "14px 22px",
                borderRadius: 12,
                border: `2px solid ${ORO_DIVINEO}`,
                background:
                  "linear-gradient(145deg, #4a148c 0%, #6a1b9a 40%, #311b92 100%)",
                color: "#fff",
                fontSize: 12,
                fontWeight: 700,
                letterSpacing: 3,
                textTransform: "uppercase",
                cursor: "pointer",
                boxShadow: `0 8px 28px ${ORO_DIVINEO}44`,
              }}
            >
              PAGAR — 12.500 €
            </button>
            {pauInaugurationWhisper ? (
              <p
                style={{
                  marginTop: 10,
                  maxWidth: 440,
                  fontSize: 13,
                  lineHeight: 1.55,
                  fontStyle: "italic",
                  color: "#4a3428",
                }}
              >
                PAU · {pauInaugurationWhisper}
              </p>
            ) : null}
          </div>
          <div style={{ marginTop: 10 }}>
            <button
              type="button"
              onClick={onLafayetteStripeCharge}
              style={{
                width: "100%",
                maxWidth: 440,
                padding: "10px 18px",
                borderRadius: 10,
                border: "1px solid rgba(0,0,0,0.2)",
                background: "rgba(255,255,255,0.75)",
                color: "#26201A",
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: 2,
                textTransform: "uppercase",
                cursor: "pointer",
              }}
            >
              Contrato Lafayette (Stripe)
            </button>
          </div>
          <p
            style={{
              marginTop: 14,
              fontSize: 12,
              letterSpacing: 1,
              color: "#5c4f3d",
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
                borderBottom: `1px solid ${ORO_DIVINEO}`,
              }}
            >
              {SOVEREIGN_FIT_LABEL}
            </a>
            <span style={{ opacity: 0.9 }}> · checkout Divineo V11 → abvetos.com</span>
          </p>
        </section>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            padding: "4px 20px 14px",
          }}
        >
          <MirrorSnap enabled={pauStarted} district={activeDistrict} onSnap={theSnap} />
        </div>

        <OfrendaOverlay
          elasticLabel={elasticLabel}
          julesLane={julesLane}
          onOfrenda={onOfrenda}
          headerExtra={
            <button
              type="button"
              onClick={() => void postBetaWaitlist()}
              style={{
                marginTop: 14,
                padding: "8px 18px",
                fontSize: 10,
                letterSpacing: 2,
                textTransform: "uppercase",
                color: "#C5A46D",
                background: "rgba(0,0,0,0.5)",
                border: "1px solid #C5A46D",
                borderRadius: 999,
                cursor: "pointer",
              }}
            >
              Únete a la beta
            </button>
          }
        />

        <motion.div
          className="app-pau-row"
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
      </div>
    </div>
  );
}
