import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import RealTimeAvatar from "./components/RealTimeAvatar";
import { ORO_DIVINEO, SOVEREIGN_FIT_LABEL } from "./divineo/divineoV11Config";
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
  const [paymentVerified, setPaymentVerified] = useState(true);
  const [paymentLockMessage, setPaymentLockMessage] = useState(
    "Sovereign Protocol Restricted - Contact Architect for Reactivation",
  );

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
        setPaymentVerified(h.payment_verified !== false);
        setPaymentLockMessage(
          h.payment_lock_message?.trim() ||
            "Sovereign Protocol Restricted - Contact Architect for Reactivation",
        );
        setJulesLane(
          `Jules · ${h.service ?? "omega"} · ${h.product_lane ?? "tryonyou_v10_omega"}`,
        );
        return;
      }
      setMirrorPoweredOn(true);
      setPaymentVerified(false);
      setPaymentLockMessage("Sovereign Protocol Restricted - Contact Architect for Reactivation");
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
    if (!paymentVerified) {
      window.alert(paymentLockMessage);
      return;
    }
    if (!mirrorPoweredOn) {
      window.alert("Le miroir est momentanément suspendu par contrôle distant.");
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
    const copy: Record<Exclude<OfrendaKey, "selection">, string> = {
      reserve: "QR cabine VIP — Lafayette, essai en courtoisie Divineo.",
      combo: "Lignes alternatives chargées — composition Zero-Size.",
      save: "Silhouette enregistrée sous protocole chiffré (aucune taille exposée).",
      share: "Partage généré — métadonnées d’ajustage neutralisées.",
    };
    window.alert(copy[key]);
  };

  const theSnap = () => {
    if (!pauStarted || !mirrorPoweredOn || !paymentVerified) return;
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
    <div
      className="app-root"
      style={{
        background: "linear-gradient(145deg, #F5F5DC 0%, #FFFFFF 38%, #D3B26A 100%)",
        color: "#111111",
      }}
    >
      <div className="app-stage" aria-hidden />

      <div className="app-ui">
        {!paymentVerified ? (
          <section
            style={{
              maxWidth: 960,
              margin: "18px auto 0",
              border: `1px solid ${ORO_DIVINEO}`,
              borderRadius: 14,
              background: "rgba(0,0,0,0.86)",
              color: ORO_DIVINEO,
              padding: "14px 18px",
              textAlign: "center",
              letterSpacing: 1.3,
              textTransform: "uppercase",
              fontSize: 12,
            }}
            role="status"
            aria-live="polite"
          >
            Error 402 · {paymentLockMessage}
          </section>
        ) : null}
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
            Espejo digital en ajuste soberano real. Sin probadores crueles, sin etiquetas que hieren.
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
              onChange={(e) => setEmailHero(e.target.value)}
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
            disabled={!pauStarted || !mirrorPoweredOn || !paymentVerified}
            onClick={theSnap}
            title={
              !paymentVerified
                ? paymentLockMessage
                : !mirrorPoweredOn
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
              opacity: pauStarted && mirrorPoweredOn && paymentVerified ? 1 : 0.55,
              cursor: pauStarted && mirrorPoweredOn && paymentVerified ? "pointer" : "not-allowed",
            }}
          >
            <RealTimeAvatar
              variant={isMaraisNode ? "marais" : "lafayette"}
              disabled={!pauStarted || !mirrorPoweredOn || !paymentVerified}
              videoId={isMaraisNode ? "marais-v10-omega" : "pau-lafayette-v10"}
            />
          </button>
        </motion.div>
      </div>
    </div>
  );
}
