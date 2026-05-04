import { useEffect, useMemo, useRef, useState, type CSSProperties, type FormEvent } from "react";
import { motion } from "framer-motion";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import { PauFloatingGuide } from "./components/PauFloatingGuide";
import { PreScanHook } from "./components/PreScanHook";
import RealTimeAvatar from "./components/RealTimeAvatar";
import { ORO_DIVINEO, SOVEREIGN_FIT_LABEL } from "./divineo/divineoV11Config";
import { getDivineoCheckoutUrl } from "./divineo/envBootstrap";
import { enforceV9IdentityLabel } from "./lib/privacyFirewall";
import {
  initFirebaseApplet,
  initFirebaseAnalytics,
  initFirebaseAppCheckIfConfigured,
} from "./lib/firebaseApplet";
import { trackCoreEvent } from "./lib/coreEngineClient";
import { fetchJulesHealth, postMirrorSnap } from "./lib/julesClient";
import { SALES_COPY, SUPPORTED_LOCALES, type AppLocale } from "./locales/salesCopy";
import "./index.css";
import "./App.css";

/** Nodos parisinos autorizados para P.A.U. (Lafayette / Marais). */
const PAU_POSTAL_NODES = new Set(["75009", "75004"]);

/** Estado operativo bunker / preview (narrativa V10). */
const OPERATIONAL_STATE_DIAMANTE = "DIAMANTE" as const;

const SECTION_KICKERS: Record<
  AppLocale,
  {
    hero: string;
    problem: string;
    solution: string;
    benefits: string;
    technology: string;
    trust: string;
    demo: string;
    finalCta: string;
    ethics: string;
    footer: string;
    heroPanel: string;
    pilots: string;
    valuation: string;
  }
> = {
  fr: {
    hero: "Retail enterprise",
    problem: "Pourquoi maintenant",
    solution: "Comment cela fonctionne",
    benefits: "Impact business",
    technology: "Digital Fit Engine",
    trust: "Preuve prête pour validation interne",
    demo: "Conversation commerciale",
    finalCta: "Décision pilotée par le business case",
    ethics: "Confiance, gouvernance, souveraineté",
    footer: "Identité légale",
    heroPanel: "Pilot desk",
    pilots: "Réseau pilote",
    valuation: "Valorisation IP",
  },
  en: {
    hero: "Enterprise retail",
    problem: "Why now",
    solution: "How it works",
    benefits: "Business impact",
    technology: "Digital Fit Engine",
    trust: "Proof ready for internal validation",
    demo: "Commercial conversation",
    finalCta: "Decision shaped by the business case",
    ethics: "Trust, governance, sovereignty",
    footer: "Legal identity",
    heroPanel: "Pilot desk",
    pilots: "Pilot network",
    valuation: "IP valuation",
  },
  es: {
    hero: "Retail enterprise",
    problem: "Por qué ahora",
    solution: "Cómo funciona",
    benefits: "Impacto de negocio",
    technology: "Digital Fit Engine",
    trust: "Prueba preparada para validación interna",
    demo: "Conversación comercial",
    finalCta: "Decisión guiada por el business case",
    ethics: "Confianza, gobernanza, soberanía",
    footer: "Identidad legal",
    heroPanel: "Pilot desk",
    pilots: "Red piloto",
    valuation: "Valoración IP",
  },
};

const STATIC_COPY: Record<
  AppLocale,
  {
    pilotPanelTitle: string;
    pilotPanelBody: string;
    pilotSlotPlaceholder: string;
    reserveSlot: string;
    betaButton: string;
    liveSystem: string;
    monitoring: string;
    districtLafayette: string;
    districtMarais: string;
    districtFallback: string;
    districtLabel: string;
    heroSecondary: string;
    demoPrimaryMarketPlaceholder: string;
    demoVolumePlaceholder: string;
    demoHorizonPlaceholder: string;
    demoChallengePlaceholder: string;
    pilotBannerIcon: string;
    pilotsHeading: string;
    manifesto: string;
    ethicsIcon: string;
    operationalAlertTitle: string;
  }
> = {
  fr: {
    pilotPanelTitle: "Desk d'activation pour pilotes retail",
    pilotPanelBody:
      "Coordination live avec Jules, accès souverain PAU et signal opérationnel prêt pour les équipes e-commerce, innovation et omnicanal.",
    pilotSlotPlaceholder: "prenom.nom@entreprise.com",
    reserveSlot: "Réserver un slot pilote",
    betaButton: "Rejoindre la bêta",
    liveSystem: "Système live",
    monitoring: "Monitoring",
    districtLafayette: "Galeries Lafayette · 75009",
    districtMarais: "BHV Marais · 75004",
    districtFallback: "Réseau souverain TRYONYOU",
    districtLabel: "District actif",
    heroSecondary: "Sovereign Fit",
    demoPrimaryMarketPlaceholder: "France, Europe, MENA…",
    demoVolumePlaceholder: "Ex. 250k commandes / mois",
    demoHorizonPlaceholder: "Ex. Pilote sous 6 semaines",
    demoChallengePlaceholder: "Retours, sizing, confiance produit, conversion PDP…",
    pilotBannerIcon: "✦",
    pilotsHeading: "Présence opérationnelle et expansion pilotée",
    manifesto: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026",
    ethicsIcon: "◈",
    operationalAlertTitle: "État opérationnel",
  },
  en: {
    pilotPanelTitle: "Activation desk for retail pilots",
    pilotPanelBody:
      "Live coordination with Jules, sovereign PAU access and operational signal ready for e-commerce, innovation and omnichannel teams.",
    pilotSlotPlaceholder: "name@company.com",
    reserveSlot: "Reserve a pilot slot",
    betaButton: "Join the beta",
    liveSystem: "Live system",
    monitoring: "Monitoring",
    districtLafayette: "Galeries Lafayette · 75009",
    districtMarais: "BHV Marais · 75004",
    districtFallback: "TRYONYOU sovereign network",
    districtLabel: "Active district",
    heroSecondary: "Sovereign Fit",
    demoPrimaryMarketPlaceholder: "France, Europe, MENA…",
    demoVolumePlaceholder: "E.g. 250k orders / month",
    demoHorizonPlaceholder: "E.g. Pilot in 6 weeks",
    demoChallengePlaceholder: "Returns, sizing, product confidence, PDP conversion…",
    pilotBannerIcon: "✦",
    pilotsHeading: "Operational presence and controlled expansion",
    manifesto: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026",
    ethicsIcon: "◈",
    operationalAlertTitle: "Operational status",
  },
  es: {
    pilotPanelTitle: "Activation desk para pilotos retail",
    pilotPanelBody:
      "Coordinación live con Jules, acceso soberano PAU y señal operativa preparada para equipos de e-commerce, innovación y omnicanalidad.",
    pilotSlotPlaceholder: "nombre@empresa.com",
    reserveSlot: "Reservar slot piloto",
    betaButton: "Unirse a la beta",
    liveSystem: "Sistema activo",
    monitoring: "Monitorización",
    districtLafayette: "Galeries Lafayette · 75009",
    districtMarais: "BHV Marais · 75004",
    districtFallback: "Red soberana TRYONYOU",
    districtLabel: "Distrito activo",
    heroSecondary: "Sovereign Fit",
    demoPrimaryMarketPlaceholder: "Francia, Europa, MENA…",
    demoVolumePlaceholder: "Ej. 250k pedidos / mes",
    demoHorizonPlaceholder: "Ej. Piloto en 6 semanas",
    demoChallengePlaceholder: "Devoluciones, sizing, confianza de producto, conversión PDP…",
    pilotBannerIcon: "✦",
    pilotsHeading: "Presencia operativa y expansión controlada",
    manifesto: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026",
    ethicsIcon: "◈",
    operationalAlertTitle: "Estado operativo",
  },
};

type BunkerSyncResult =
  | { ok: true; data: unknown }
  | { ok: false; error: unknown };

type DemoFormState = {
  fullName: string;
  corporateEmail: string;
  company: string;
  role: string;
  businessType: string;
  primaryMarket: string;
  volume: string;
  challenge: string;
  horizon: string;
  consent: boolean;
};

type FormStatus =
  | { type: "idle" }
  | { type: "submitting" }
  | { type: "success" }
  | { type: "error"; message: string };

type ParsedMetric = {
  numeric: boolean;
  target: number;
  decimals: number;
  prefix: string;
  suffix: string;
  raw: string;
};

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
  const safeLabel = enforceV9IdentityLabel(label);
  if (safeLabel.includes("Préférence drapé")) return "drape_bias";
  if (safeLabel.includes("Préférence tenue")) return "tension_bias";
  return "aligned";
}

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
  } catch (e) {
    console.warn("[App] postPerfectCheckout", e);
  }
}

const createInitialDemoFormState = (locale: AppLocale): DemoFormState => ({
  fullName: "",
  corporateEmail: "",
  company: "",
  role: "",
  businessType: SALES_COPY[locale].demoForm.businessTypeOptions[0] ?? "",
  primaryMarket: "",
  volume: "",
  challenge: "",
  horizon: "",
  consent: false,
});

function parseMetricValue(raw: string): ParsedMetric {
  const trimmed = raw.trim();
  const match = trimmed.match(/-?[\d\s.,]+/);
  if (!match || match.index == null) {
    return {
      numeric: false,
      target: 0,
      decimals: 0,
      prefix: "",
      suffix: "",
      raw: trimmed,
    };
  }

  const numericToken = match[0];
  const sanitized = numericToken.replace(/\s+/g, "").replace(",", ".");
  const target = Number.parseFloat(sanitized);

  if (Number.isNaN(target)) {
    return {
      numeric: false,
      target: 0,
      decimals: 0,
      prefix: "",
      suffix: "",
      raw: trimmed,
    };
  }

  const decimals = sanitized.includes(".") ? sanitized.split(".")[1].length : 0;

  return {
    numeric: true,
    target,
    decimals,
    prefix: trimmed.slice(0, match.index),
    suffix: trimmed.slice(match.index + numericToken.length),
    raw: trimmed,
  };
}

function formatMetricValue(value: number, parsed: ParsedMetric, locale: AppLocale): string {
  if (!parsed.numeric) return parsed.raw;
  const formatter = new Intl.NumberFormat(locale, {
    minimumFractionDigits: parsed.decimals,
    maximumFractionDigits: parsed.decimals,
  });
  return `${parsed.prefix}${formatter.format(value)}${parsed.suffix}`;
}

export default function App() {
  const pauSovereignBoot = useRef(false);
  if (!pauSovereignBoot.current) {
    pauSovereignBoot.current = true;
    forceUserCheckIfPilotCold();
  }

  const [locale, setLocale] = useState<AppLocale>("fr");
  const [elasticLabel, setElasticLabel] = useState("V9 Identity");
  const [julesLane, setJulesLane] = useState<string>("Orchestration Jules…");
  const [emailHero, setEmailHero] = useState<string>("");
  const [mirrorPoweredOn, setMirrorPoweredOn] = useState(true);
  const [debtMessage, setDebtMessage] = useState<string>("");
  const [demoForm, setDemoForm] = useState<DemoFormState>(() => createInitialDemoFormState("fr"));
  const [formStatus, setFormStatus] = useState<FormStatus>({ type: "idle" });
  const [preScanVisible, setPreScanVisible] = useState(false);
  const [pendingSnap, setPendingSnap] = useState(false);
  const [metricValues, setMetricValues] = useState<string[]>(() =>
    SALES_COPY.fr.trust.metrics.map((metric) => metric.value),
  );

  /** Re-render al cambiar UserCheck en consola / initPauAlpha; tick ligero. */
  const [pauDistrictTick, setPauDistrictTick] = useState(0);

  const appRef = useRef<HTMLDivElement | null>(null);
  const metricRefs = useRef<Array<HTMLElement | null>>([]);
  const animatedMetricsRef = useRef<Set<number>>(new Set());

  /** window.UserCheck truthy, o nodo postal 75009 / 75004 (Lafayette / Marais) → Pau activo. */
  const pauStarted = isPauAuthorized();
  const copy = SALES_COPY[locale];
  const kickers = SECTION_KICKERS[locale];
  const staticCopy = STATIC_COPY[locale];

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

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

  /** Galeries Lafayette (75009) y BHV Marais (75004) → estado DIAMANTE + relanzar initPauAlpha. */
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
        setDebtMessage(h.debt_message ?? "");
        setJulesLane(`Jules · ${h.service ?? "omega"} · ${h.product_lane ?? "tryonyou_v10_omega"}`);
        return;
      }
      setMirrorPoweredOn(true);
      setDebtMessage("");
      setJulesLane("Jules · prévisualisation locale (API Python non joignable sur ce port)");
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
      if (typeof lab === "string" && lab.length > 0) {
        setElasticLabel(enforceV9IdentityLabel(lab));
      }
    };
    window.addEventListener("tryonyou:fit", onFit);
    return () => window.removeEventListener("tryonyou:fit", onFit);
  }, []);

  useEffect(() => {
    const nodes = Array.from(appRef.current?.querySelectorAll<HTMLElement>(".reveal") ?? []);
    if (nodes.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
          }
        });
      },
      { threshold: 0.16, rootMargin: "0px 0px -6% 0px" },
    );

    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, [locale]);

  useEffect(() => {
    setDemoForm((current) => ({
      ...createInitialDemoFormState(locale),
      fullName: current.fullName,
      corporateEmail: current.corporateEmail,
      company: current.company,
      role: current.role,
      primaryMarket: current.primaryMarket,
      volume: current.volume,
      challenge: current.challenge,
      horizon: current.horizon,
      consent: current.consent,
    }));
    setMetricValues(SALES_COPY[locale].trust.metrics.map((metric) => metric.value));
    animatedMetricsRef.current.clear();
    setFormStatus({ type: "idle" });
  }, [locale]);

  const animateMetric = (index: number) => {
    const parsed = parseMetricValue(copy.trust.metrics[index]?.value ?? "");
    if (!parsed.numeric) {
      setMetricValues((current) => {
        const next = [...current];
        next[index] = parsed.raw;
        return next;
      });
      return;
    }

    const duration = 1400;
    let startTime = 0;

    const step = (timestamp: number) => {
      if (startTime === 0) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const currentValue = parsed.target * eased;

      setMetricValues((current) => {
        const next = [...current];
        next[index] = formatMetricValue(currentValue, parsed, locale);
        return next;
      });

      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };

    window.requestAnimationFrame(step);
  };

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const index = Number((entry.target as HTMLElement).dataset.metricIndex);
          if (Number.isNaN(index) || animatedMetricsRef.current.has(index)) return;
          animatedMetricsRef.current.add(index);
          animateMetric(index);
        });
      },
      { threshold: 0.45 },
    );

    metricRefs.current.forEach((node) => {
      if (node) observer.observe(node);
    });

    return () => observer.disconnect();
  }, [locale, copy.trust.metrics]);

  const particleBlueprints = useMemo<CSSProperties[]>(
    () => [
      { left: "4%", width: 6, height: 6, animationDuration: "20s", animationDelay: "0s" },
      { left: "12%", width: 10, height: 10, animationDuration: "26s", animationDelay: "-6s" },
      { left: "19%", width: 4, height: 4, animationDuration: "18s", animationDelay: "-4s" },
      { left: "28%", width: 12, height: 12, animationDuration: "28s", animationDelay: "-12s" },
      { left: "34%", width: 8, height: 8, animationDuration: "24s", animationDelay: "-8s" },
      { left: "43%", width: 14, height: 14, animationDuration: "32s", animationDelay: "-10s" },
      { left: "51%", width: 6, height: 6, animationDuration: "22s", animationDelay: "-3s" },
      { left: "60%", width: 9, height: 9, animationDuration: "27s", animationDelay: "-15s" },
      { left: "68%", width: 5, height: 5, animationDuration: "17s", animationDelay: "-7s" },
      { left: "75%", width: 11, height: 11, animationDuration: "29s", animationDelay: "-11s" },
      { left: "82%", width: 7, height: 7, animationDuration: "23s", animationDelay: "-5s" },
      { left: "91%", width: 13, height: 13, animationDuration: "31s", animationDelay: "-14s" },
    ],
    [],
  );

  const navLinks = useMemo(
    () => [
      { id: "home", label: copy.nav.home },
      { id: "technology", label: copy.nav.technology },
      { id: "solution", label: copy.nav.solutions },
      { id: "pilots", label: copy.nav.pilots },
      { id: "about", label: copy.nav.about },
      { id: "legal", label: copy.nav.legal },
    ],
    [copy.nav],
  );

  const onOfrenda = (key: OfrendaKey) => {
    if (!mirrorPoweredOn) {
      window.alert(debtMessage || "Le miroir est momentanément suspendu par contrôle distant.");
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
    const messageCopy: Record<AppLocale, Record<Exclude<OfrendaKey, "selection">, string>> = {
      fr: {
        reserve: "QR cabine VIP — Lafayette, essai en courtoisie Divineo.",
        combo: "Lignes alternatives chargées — composition Zero-Size.",
        save: "Silhouette enregistrée sous protocole chiffré (aucune taille exposée).",
        share: "Partage généré — métadonnées d’ajustage neutralisées.",
        balmain: "Balmain activado bajo protocolo soberano con identidad V9.",
      },
      en: {
        reserve: "VIP fitting QR — Lafayette, Divineo courtesy session enabled.",
        combo: "Alternative lines loaded — Zero-Size composition ready.",
        save: "Silhouette stored under encrypted protocol (no visible size exposed).",
        share: "Share generated — fit metadata neutralized.",
        balmain: "Balmain enabled under sovereign protocol with V9 identity.",
      },
      es: {
        reserve: "QR de cabina VIP — Lafayette, prueba en cortesía Divineo.",
        combo: "Líneas alternativas cargadas — composición Zero-Size.",
        save: "Silueta guardada bajo protocolo cifrado (sin talla expuesta).",
        share: "Compartido generado — metadatos de ajuste neutralizados.",
        balmain: "Balmain activado bajo protocolo soberano con identidad V9.",
      },
    };
    window.alert(messageCopy[locale][key]);
  };

  const theSnap = () => {
    if (!pauStarted || !mirrorPoweredOn) return;
    void (async () => {
      await trackCoreEvent("silhouette_scan_intent", {
        fabric_sensation: elasticLabel,
        fabric_fit_verdict: elasticLabelToVerdict(elasticLabel),
      });
      const j = await postMirrorSnap(elasticLabel, elasticLabelToVerdict(elasticLabel));
      const fallbackMessage: Record<AppLocale, string> = {
        fr: "The Snap — votre ligne trouve son équilibre. Le drapé répond avec élégance, sans mesure visible.",
        en: "The Snap — your silhouette finds its balance. The drape answers with elegance, without exposing size.",
        es: "The Snap — tu silueta encuentra su equilibrio. El drapeado responde con elegancia, sin exponer talla.",
      };
      const msg = j?.jules_msg ?? fallbackMessage[locale];
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

  const scrollToId = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleDemoSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!demoForm.consent) {
      setFormStatus({
        type: "error",
        message: `${copy.demoForm.error} ${copy.demoForm.consentHint}`,
      });
      return;
    }

    setFormStatus({ type: "submitting" });

    const payload = {
      ...demoForm,
      locale,
      source: "b2b_conversion_landing",
      product_lane: julesLane,
      district: activeDistrict || null,
      pau_authorized: pauStarted,
      mirror_powered_on: mirrorPoweredOn,
      ts: new Date().toISOString(),
      user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "",
    };

    try {
      await trackCoreEvent("b2b_demo_form_submit", {
        locale,
        business_type: demoForm.businessType,
        company: demoForm.company,
      });

      const response = await fetch("/api/v1/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(copy.demoForm.retry);
      }

      await response.json().catch(() => null);
      setFormStatus({ type: "success" });
      setDemoForm(createInitialDemoFormState(locale));
    } catch (error) {
      setFormStatus({
        type: "error",
        message: error instanceof Error ? error.message : `${copy.demoForm.error} ${copy.demoForm.retry}`,
      });
    }
  };

  const onPauOrbClick = () => {
    if (!pauStarted || !mirrorPoweredOn) return;
    setPendingSnap(true);
    setPreScanVisible(true);
  };

  const handlePreScanDismiss = () => {
    setPreScanVisible(false);
    if (!pendingSnap) return;
    setPendingSnap(false);
    theSnap();
  };

  const activeDistrictLabel = isMaraisNode
    ? staticCopy.districtMarais
    : activeDistrict === "75009"
      ? staticCopy.districtLafayette
      : staticCopy.districtFallback;

  return (
    <div ref={appRef} className="app-shell">
      <div className="app-particles" aria-hidden="true">
        {particleBlueprints.map((style, index) => (
          <span key={`particle-${index}`} className="app-particle" style={style} />
        ))}
      </div>

      <header className="site-header">
        <div className="site-header__inner">
          <a
            href="#home"
            className="brand-lockup"
            onClick={(event) => {
              event.preventDefault();
              scrollToId("home");
            }}
          >
            <span className="brand-lockup__name">TRYONYOU</span>
            <span className="brand-lockup__product">Digital Fit Engine</span>
          </a>

          <nav className="site-nav" aria-label="Primary">
            {navLinks.map((link) => (
              <a
                key={link.id}
                href={`#${link.id}`}
                className="site-nav__link"
                onClick={(event) => {
                  event.preventDefault();
                  scrollToId(link.id);
                }}
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="site-header__actions">
            <div className="locale-switch" aria-label={copy.localeLabel}>
              {SUPPORTED_LOCALES.map((supportedLocale) => (
                <button
                  key={supportedLocale}
                  type="button"
                  className="locale-switch__button"
                  data-active={locale === supportedLocale}
                  onClick={() => setLocale(supportedLocale)}
                >
                  {supportedLocale}
                </button>
              ))}
            </div>

            <button
              type="button"
              className="button button--primary button--compact"
              onClick={() => scrollToId("demo")}
            >
              {copy.nav.demo}
            </button>
          </div>
        </div>
      </header>

      <main className="site-main">
        <section id="home" className="section section--hero">
          <div className="section-shell hero-grid">
            <div className="hero-copy reveal">
              <p className="section-kicker">{kickers.hero}</p>
              <h1>{copy.hero.title}</h1>
              <p className="section-lead">{copy.hero.lead}</p>

              <div className="hero-actions">
                <button
                  type="button"
                  className="button button--primary"
                  onClick={() => scrollToId("demo")}
                >
                  {copy.hero.cta}
                </button>
                <a
                  className="button button--secondary"
                  href={getDivineoCheckoutUrl()}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {staticCopy.heroSecondary}
                </a>
              </div>

              <div className="trust-strip">
                {copy.hero.trustStrip.map((item) => (
                  <div key={item} className="trust-strip__item">
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <aside className="hero-panel reveal">
              <div className="hero-panel__inner">
                <p className="hero-panel__eyebrow">{kickers.heroPanel}</p>
                <h2>{staticCopy.pilotPanelTitle}</h2>
                <p>{staticCopy.pilotPanelBody}</p>

                <ul className="module-list module-list--stacked" aria-label={staticCopy.monitoring}>
                  <li>
                    <span className="technology-module__dot" aria-hidden="true" />
                    {staticCopy.liveSystem} · {julesLane}
                  </li>
                  <li>
                    <span className="technology-module__dot" aria-hidden="true" />
                    {staticCopy.districtLabel} · {activeDistrictLabel}
                  </li>
                  <li>
                    <span className="technology-module__dot" aria-hidden="true" />
                    {copy.technology.pauLabel}
                  </li>
                </ul>

                {!mirrorPoweredOn && debtMessage ? (
                  <div className="form-feedback form-feedback--error" role="alert">
                    <strong>{staticCopy.operationalAlertTitle}</strong>
                    <span>{debtMessage}</span>
                  </div>
                ) : null}

                <div className="form-field">
                  <span>{copy.demoForm.fieldLabels.corporateEmail}</span>
                  <input
                    type="email"
                    value={emailHero}
                    onChange={(event) => setEmailHero(event.target.value)}
                    placeholder={staticCopy.pilotSlotPlaceholder}
                    autoComplete="email"
                  />
                </div>

                <div className="hero-actions">
                  <button type="button" className="button button--primary button--compact" onClick={() => void onHeroSubmit()}>
                    {staticCopy.reserveSlot}
                  </button>
                  <button
                    type="button"
                    className="button button--secondary button--compact"
                    onClick={() => void postBetaWaitlist()}
                  >
                    {staticCopy.betaButton}
                  </button>
                </div>
                <p>{SOVEREIGN_FIT_LABEL}</p>
              </div>
            </aside>
          </div>
        </section>

        <section className="section" id="problem">
          <div className="section-shell">
            <div className="section-copy section-copy--single reveal">
              <p className="section-kicker">{kickers.problem}</p>
              <h2>{copy.problem.title}</h2>
              <p className="section-lead">{copy.problem.body}</p>
              <p className="section-emphasis">{copy.problem.closing}</p>
            </div>
          </div>
        </section>

        <section className="section" id="solution">
          <div className="section-shell">
            <div className="section-copy reveal">
              <p className="section-kicker">{kickers.solution}</p>
              <h2>{copy.solution.title}</h2>
              <p className="section-lead">{copy.solution.support}</p>
            </div>

            <div className="steps-grid reveal">
              {copy.solution.steps.map((step, index) => (
                <article key={step.title} className="content-card content-card--step">
                  <p className="content-card__eyebrow">{copy.nav.solutions}</p>
                  <p className="content-card__index">0{index + 1}</p>
                  <h3>{step.title}</h3>
                  <p>{step.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section" id="benefits">
          <div className="section-shell">
            <div className="section-copy reveal">
              <p className="section-kicker">{kickers.benefits}</p>
              <h2>{copy.benefits.title}</h2>
            </div>

            <div className="benefits-grid reveal">
              {copy.benefits.cards.map((card) => (
                <article key={card.title} className="content-card">
                  <p className="content-card__eyebrow">{card.eyebrow}</p>
                  <h3>{card.title}</h3>
                  <p>{card.body}</p>
                </article>
              ))}
            </div>

            <p className="section-footnote reveal">{copy.benefits.closing}</p>
          </div>
        </section>

        <section className="section" id="technology">
          <div className="section-shell technology-grid">
            <div className="section-copy reveal">
              <p className="section-kicker">{kickers.technology}</p>
              <h2>{copy.technology.title}</h2>
              <p className="section-lead">{copy.technology.body}</p>
            </div>

            <aside className="technology-panel reveal">
              <div className="technology-panel__header">
                <p className="technology-panel__eyebrow">{copy.technology.pauLabel}</p>
                <p>{elasticLabel}</p>
              </div>
              <div className="technology-modules">
                {copy.technology.modules.map((module) => (
                  <div key={module} className="technology-module">
                    <span className="technology-module__dot" aria-hidden="true" />
                    <span>{module}</span>
                  </div>
                ))}
              </div>
              <p>{julesLane}</p>
            </aside>
          </div>
        </section>

        <section className="section" id="trust">
          <div className="section-shell">
            <div className="section-copy reveal">
              <p className="section-kicker">{kickers.trust}</p>
              <h2>{copy.trust.title}</h2>
              <p className="section-lead">{copy.trust.body}</p>
            </div>

            <div className="metrics-grid reveal">
              {copy.trust.metrics.map((metric, index) => (
                <article
                  key={`${metric.label}-${index}`}
                  ref={(node) => {
                    metricRefs.current[index] = node;
                  }}
                  className="metric-card"
                  data-metric-index={index}
                >
                  <p className="metric-card__value metric-card__value--animated">{metricValues[index] ?? metric.value}</p>
                  <p className="metric-card__label">{metric.label}</p>
                </article>
              ))}
            </div>

            <p className="section-footnote reveal">{copy.trust.note}</p>

            <div id="pilots" className="reveal">
              <p className="section-kicker">{kickers.pilots}</p>
              <div className="expansion-banner">
                <div className="expansion-banner__icon" aria-hidden="true">
                  {staticCopy.pilotBannerIcon}
                </div>
                <div className="expansion-banner__copy">
                  <h3>{copy.expansion.bannerTitle}</h3>
                  <p>{copy.expansion.bannerBody}</p>
                </div>
              </div>

              <div className="section-copy section-copy--single">
                <p className="section-lead">{staticCopy.pilotsHeading}</p>
              </div>

              <div className="expansion-grid">
                {copy.expansion.locations.map((location) => (
                  <article
                    key={`${location.name}-${location.district}`}
                    className={`expansion-node ${
                      location.status === "active" ? "expansion-node--active" : "expansion-node--pending"
                    }`}
                  >
                    <span className="expansion-node__badge">
                      {location.status === "active"
                        ? copy.expansion.activeBadge
                        : copy.expansion.pendingBadge}
                    </span>
                    <h3 className="expansion-node__name">{location.name}</h3>
                    <p className="expansion-node__district">{location.district}</p>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="section section--demo" id="demo">
          <div className="section-shell demo-grid">
            <div className="section-copy reveal">
              <p className="section-kicker">{kickers.demo}</p>
              <h2>{copy.demoForm.title}</h2>
              <p className="section-lead">{copy.demoForm.support}</p>
              <p className="section-emphasis">{copy.finalCta.microcopy}</p>
            </div>

            <form className="demo-form reveal" onSubmit={handleDemoSubmit}>
              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.fullName}</span>
                <input
                  type="text"
                  value={demoForm.fullName}
                  onChange={(event) =>
                    setDemoForm((current) => ({ ...current, fullName: event.target.value }))
                  }
                  autoComplete="name"
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.corporateEmail}</span>
                <input
                  type="email"
                  value={demoForm.corporateEmail}
                  onChange={(event) =>
                    setDemoForm((current) => ({ ...current, corporateEmail: event.target.value }))
                  }
                  autoComplete="email"
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.company}</span>
                <input
                  type="text"
                  value={demoForm.company}
                  onChange={(event) =>
                    setDemoForm((current) => ({ ...current, company: event.target.value }))
                  }
                  autoComplete="organization"
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.role}</span>
                <input
                  type="text"
                  value={demoForm.role}
                  onChange={(event) => setDemoForm((current) => ({ ...current, role: event.target.value }))}
                  autoComplete="organization-title"
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.businessType}</span>
                <select
                  value={demoForm.businessType}
                  onChange={(event) =>
                    setDemoForm((current) => ({ ...current, businessType: event.target.value }))
                  }
                  required
                >
                  {copy.demoForm.businessTypeOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>

              <label className="form-field">
                <span>
                  {copy.demoForm.fieldLabels.primaryMarket}
                  <em>{copy.demoForm.optionalLabel}</em>
                </span>
                <input
                  type="text"
                  value={demoForm.primaryMarket}
                  onChange={(event) =>
                    setDemoForm((current) => ({ ...current, primaryMarket: event.target.value }))
                  }
                  placeholder={staticCopy.demoPrimaryMarketPlaceholder}
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.volume}</span>
                <input
                  type="text"
                  value={demoForm.volume}
                  onChange={(event) => setDemoForm((current) => ({ ...current, volume: event.target.value }))}
                  placeholder={staticCopy.demoVolumePlaceholder}
                  required
                />
              </label>

              <label className="form-field">
                <span>{copy.demoForm.fieldLabels.horizon}</span>
                <input
                  type="text"
                  value={demoForm.horizon}
                  onChange={(event) => setDemoForm((current) => ({ ...current, horizon: event.target.value }))}
                  placeholder={staticCopy.demoHorizonPlaceholder}
                  required
                />
              </label>

              <label className="form-field form-field--full">
                <span>{copy.demoForm.fieldLabels.challenge}</span>
                <textarea
                  rows={5}
                  value={demoForm.challenge}
                  onChange={(event) =>
                    setDemoForm((current) => ({ ...current, challenge: event.target.value }))
                  }
                  placeholder={staticCopy.demoChallengePlaceholder}
                  required
                />
              </label>

              <label className="consent-field form-field--full">
                <input
                  type="checkbox"
                  checked={demoForm.consent}
                  onChange={(event) =>
                    setDemoForm((current) => ({ ...current, consent: event.target.checked }))
                  }
                  required
                />
                <span>
                  {copy.demoForm.fieldLabels.consent}
                  <small>{copy.demoForm.consentHint}</small>
                </span>
              </label>

              <div className="form-actions form-field--full">
                <button
                  type="submit"
                  className="button button--primary"
                  disabled={formStatus.type === "submitting"}
                >
                  {formStatus.type === "submitting" ? copy.demoForm.submitting : copy.demoForm.submit}
                </button>
              </div>

              {formStatus.type === "success" ? (
                <div className="form-feedback form-feedback--success form-field--full" role="status">
                  <strong>{copy.demoForm.successTitle}</strong>
                  <span>{copy.demoForm.successBody}</span>
                </div>
              ) : null}

              {formStatus.type === "error" ? (
                <div className="form-feedback form-feedback--error form-field--full" role="alert">
                  <strong>{copy.demoForm.error}</strong>
                  <span>{formStatus.message}</span>
                </div>
              ) : null}
            </form>
          </div>
        </section>

        <section className="section" id="final-cta">
          <div className="section-shell cta-grid">
            <div className="section-copy reveal">
              <p className="section-kicker">{kickers.finalCta}</p>
              <h2>{copy.finalCta.title}</h2>
              <p className="section-lead">{copy.finalCta.microcopy}</p>
            </div>

            <div className="hero-panel reveal">
              <div className="hero-panel__inner">
                <p className="hero-panel__eyebrow">{copy.finalCta.cta}</p>
                <h2>{copy.nav.demo}</h2>
                <p>{copy.finalCta.microcopy}</p>
                <div className="hero-actions">
                  <button
                    type="button"
                    className="button button--primary"
                    onClick={() => scrollToId("demo")}
                  >
                    {copy.finalCta.cta}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="section" id="about">
          <div className="section-shell">
            <div className="section-copy reveal">
              <p className="section-kicker">{kickers.ethics}</p>
              <h2>{copy.ethics.sectionTitle}</h2>
            </div>

            <div className="ethics-grid reveal">
              {copy.ethics.principles.map((principle) => (
                <article key={principle.title} className="content-card ethics-card">
                  <div className="ethics-card__icon" aria-hidden="true">
                    {staticCopy.ethicsIcon}
                  </div>
                  <h3>{principle.title}</h3>
                  <p>{principle.body}</p>
                </article>
              ))}
            </div>

            <div className="ethics-seal reveal">
              <span className="ethics-seal__mark" aria-hidden="true">
                {staticCopy.ethicsIcon}
              </span>
              <p>{copy.ethics.seal}</p>
            </div>
          </div>
        </section>

        <section className="section" id="valuation">
          <div className="section-shell">
            <div className="section-copy reveal">
              <p className="section-kicker">{kickers.valuation}</p>
              <h2>{copy.valuation.sectionTitle}</h2>
              <p className="section-lead">{copy.valuation.lead}</p>
            </div>

            <div className="valuation-grid reveal">
              <article className="metric-card">
                <p className="metric-card__value">{new Intl.NumberFormat(locale, { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(33240 * 12)}</p>
                <p className="metric-card__label">{copy.valuation.arrLabel}</p>
              </article>
              <article className="metric-card">
                <p className="metric-card__value">8.5×</p>
                <p className="metric-card__label">{copy.valuation.multiplierLabel}</p>
              </article>
              <article className="metric-card metric-card--highlight">
                <p className="metric-card__value">{new Intl.NumberFormat(locale, { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(33240 * 12 * 8.5)}</p>
                <p className="metric-card__label">{copy.valuation.valuationLabel}</p>
              </article>
              <article className="metric-card">
                <p className="metric-card__value">6 {locale === "fr" ? "mois" : locale === "es" ? "meses" : "months"}</p>
                <p className="metric-card__label">{copy.valuation.exitLabel}</p>
              </article>
            </div>

            <div className="valuation-assets reveal">
              <p className="section-footnote">
                {copy.valuation.assetsLabel}: Lafayette · Le Bon Marché · La Défense
              </p>
              <div className="ethics-seal">
                <span className="ethics-seal__mark" aria-hidden="true">{staticCopy.ethicsIcon}</span>
                <p>{copy.valuation.statusLabel}: READY FOR EXIT</p>
              </div>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="section-shell">
            <p className="manifesto-bottom reveal">{staticCopy.manifesto}</p>
          </div>
        </section>
      </main>

      <footer id="legal" className="site-footer">
        <div className="site-footer__inner">
          <div>
            <p className="section-kicker">{kickers.footer}</p>
            <p>{copy.footer.companyLine}</p>
          </div>
          <div className="site-footer__links">
            <a href="/legal/privacy">{copy.footer.privacy}</a>
            <a href="/legal/biometric-data">{copy.footer.biometricData}</a>
            <a href="/legal/terms">{copy.footer.terms}</a>
            <a href="/legal/cookies">{copy.footer.cookies}</a>
            <a href="/legal/security">{copy.footer.security}</a>
          </div>
        </div>
      </footer>

      <OfrendaOverlay
        elasticLabel={elasticLabel}
        julesLane={julesLane}
        onOfrenda={onOfrenda}
        locale={locale}
        headerExtra={
          <button
            type="button"
            className="button button--secondary button--compact"
            onClick={() => void postBetaWaitlist()}
          >
            {staticCopy.betaButton}
          </button>
        }
      />

      <PauFloatingGuide locale={locale} />

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
          className={isMaraisNode && pauStarted ? "app-pau app-pau--marais" : "app-pau app-pau--lafayette"}
          disabled={!pauStarted || !mirrorPoweredOn}
          onClick={onPauOrbClick}
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

      <PreScanHook visible={preScanVisible} onDismiss={handlePreScanDismiss} />
    </div>
  );
}
