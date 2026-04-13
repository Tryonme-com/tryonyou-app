import {
  type ChangeEvent,
  type FormEvent,
  type MouseEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { motion } from "framer-motion";
import { OfrendaOverlay, type OfrendaKey } from "./components/OfrendaOverlay";
import { PauFloatingGuide } from "./components/PauFloatingGuide";
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
import lafayetteCollectionRaw from "./data/lafayette_collection.json";
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

type LafayetteGarment = {
  id: string;
  brand: string;
  name: string;
  category: string;
  fabric: string;
  color: string;
  color_name: string;
  price: number;
  precision: number;
  fit_profile: string[];
  image: string;
  tag: string;
};

type LocalizedLandingContent = {
  navLinks: readonly { label: string; href: string }[];
  navCta: string;
  heroHeadline: string;
  heroSubheadline: string;
  heroTrust: string;
  problemTitle: string;
  problemBody: string;
  solutionTitle: string;
  solutionBody: string;
  resultTitle: string;
  resultBody: string;
  howItWorksTag: string;
  howItWorksTitle: string;
  howItWorksSteps: readonly string[];
  technologyTag: string;
  technologyTitle: string;
  technologyLead: string;
  technologyNarrative: string;
  metricLabels: readonly string[];
  demoTag: string;
  demoTitle: string;
  demoLead: string;
  demoFields: {
    name: string;
    company: string;
    email: string;
    role: string;
    catalog: string;
    message: string;
  };
  catalogOptions: readonly string[];
  trustTitle: string;
  trustCards: readonly {
    title: string;
    body: string;
  }[];
  pauTag: string;
  pauTitle: string;
  pauLead: string;
  pauBody: string;
  pauCapabilityTitle: string;
  pauCapabilities: readonly string[];
  pauLiveLabel: string;
  pauSnapCta: string;
  pauStatusReady: string;
  pauStatusLocked: string;
  manifestoIntro: string;
  manifestoQuoteLabel: string;
  footerDescription: string;
  footerPrivacyLabel: string;
  footerTermsLabel: string;
};

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

const BRANDS_MAESTROS = ["BALMAIN", "DIOR", "PRADA", "CHANEL", "YSL"] as const;

const LANDING_CONTENT: Record<AppLocale, LocalizedLandingContent> = {
  fr: {
    navLinks: [
      { label: "Technologie", href: "#technology" },
      { label: "Solution", href: "#solution" },
      { label: "Démo", href: "#demo" },
      { label: "Contact", href: "#contact" },
    ],
    navCta: "Demander une démo",
    heroHeadline: "Réduisez les retours mode de 85% grâce à l'IA qui prédit le fit parfait",
    heroSubheadline:
      "TryOnYou crée un jumeau numérique de chaque client pour simuler l'ajustement réel des vêtements — avant l'achat.",
    heroTrust:
      "Pilotes en cours avec retailers européens · Technologie brevetée · RGPD compliant",
    problemTitle: "Le problème",
    problemBody:
      "Les retours en e-commerce mode coûtent 550Mds€/an. 52% sont liés à un mauvais ajustement. Chaque retour érode la marge et la confiance client.",
    solutionTitle: "La solution",
    solutionBody:
      "Un jumeau numérique du client + simulation textile IA = certitude d'ajustement avant l'achat. Zéro taille classique, zéro friction.",
    resultTitle: "Le résultat",
    resultBody: "-85% retours · +25% conversion · 99,7% précision biométrique",
    howItWorksTag: "COMMENT ÇA MARCHE",
    howItWorksTitle: "Une expérience simple pour le client, un impact mesurable pour le retailer",
    howItWorksSteps: [
      "Le client se place devant le miroir ou la caméra",
      "Notre IA crée un jumeau numérique et simule les vêtements en temps réel",
      "Le client voit le résultat, choisit et achète avec certitude",
    ],
    technologyTag: "TECHNOLOGIE",
    technologyTitle: "IA de simulation textile, pas un filtre photo",
    technologyLead:
      "TryOnYou combine jumeau numérique, biométrie et simulation textile pour prédire l'ajustement réel avant l'achat.",
    technologyNarrative:
      "Conçu pour réduire les retours, augmenter la conversion et supporter des déploiements retail à grande échelle.",
    metricLabels: [
      "Retours réduits",
      "Conversion augmentée",
      "Précision biométrique",
      "Utilisateurs simultanés",
    ],
    demoTag: "DÉMO",
    demoTitle: "Demandez une démo enterprise",
    demoLead:
      "Parlez-nous de votre catalogue, de vos objectifs et de votre équipe. Nous revenons vers vous avec un plan de démonstration adapté à votre activité.",
    demoFields: {
      name: "Nom",
      company: "Entreprise",
      email: "Email professionnel",
      role: "Poste",
      catalog: "Taille du catalogue",
      message: "Message",
    },
    catalogOptions: ["<1000", "1000-10000", "10000-50000", "50000+"],
    trustTitle: "Pourquoi les retailers nous font confiance",
    trustCards: [
      {
        title: "Technologie brevetée",
        body: "PCT/EP2025/067317",
      },
      {
        title: "RGPD compliant",
        body: "Données biométriques chiffrées et éphémères",
      },
      {
        title: "Pilotes en cours",
        body: "Avec retailers européens de premier plan",
      },
      {
        title: "ROI mesurable",
        body: "Réduction retours prouvée dès le premier mois",
      },
    ],
    pauTag: "P.A.U.",
    pauTitle: "Votre assistant IA d'essayage pour guider l'expérience client",
    pauLead:
      "P.A.U. accompagne le client à chaque étape pour fluidifier l'essayage virtuel et rassurer avant achat.",
    pauBody:
      "Pensé pour le retail mode, P.A.U. aide à capturer les données nécessaires, explique le résultat et accélère la décision d'achat sans friction.",
    pauCapabilityTitle: "Ce que P.A.U. orchestre",
    pauCapabilities: [
      "Guidage client pendant le scan",
      "Assistance pendant la simulation de fit",
      "Aide à la décision avant achat",
    ],
    pauLiveLabel: "Statut live",
    pauSnapCta: "Lancer la démonstration",
    pauStatusReady: "P.A.U. autorisé et prêt à opérer.",
    pauStatusLocked: "P.A.U. attend un nœud autorisé ou un UserCheck actif.",
    manifestoIntro:
      "Une vision fondatrice, désormais ramenée à l'essentiel: remplacer l'incertitude de taille par une certitude de fit exploitable pour le retail.",
    manifestoQuoteLabel: "Vision",
    footerDescription: "Essayage virtuel IA pour le retail mode",
    footerPrivacyLabel: "Privacy Policy",
    footerTermsLabel: "Terms",
  },
  en: {
    navLinks: [
      { label: "Technology", href: "#technology" },
      { label: "Solution", href: "#solution" },
      { label: "Demo", href: "#demo" },
      { label: "Contact", href: "#contact" },
    ],
    navCta: "Request a demo",
    heroHeadline: "Reduce fashion returns by 85% with AI that predicts perfect fit",
    heroSubheadline:
      "TryOnYou creates a digital twin of each customer to simulate real garment fit — before purchase.",
    heroTrust:
      "Pilots underway with European retailers · Patented technology · GDPR compliant",
    problemTitle: "The problem",
    problemBody:
      "Fashion e-commerce returns cost €550B/year. 52% are fit-related. Each return erodes margin and customer trust.",
    solutionTitle: "The solution",
    solutionBody:
      "A digital twin of the customer + AI textile simulation = fit certainty before purchase. Zero classic sizing, zero friction.",
    resultTitle: "The result",
    resultBody: "-85% returns · +25% conversion · 99.7% biometric precision",
    howItWorksTag: "HOW IT WORKS",
    howItWorksTitle: "Simple for the customer, commercially measurable for the retailer",
    howItWorksSteps: [
      "The customer stands in front of the mirror or camera",
      "Our AI creates a digital twin and simulates garments in real time",
      "The customer sees the result, chooses and buys with certainty",
    ],
    technologyTag: "TECHNOLOGY",
    technologyTitle: "Textile simulation AI, not a photo filter",
    technologyLead:
      "TryOnYou combines digital twin creation, biometrics and textile simulation to predict real garment fit before purchase.",
    technologyNarrative:
      "Built to cut returns, increase conversion and support enterprise-scale retail deployments.",
    metricLabels: [
      "Returns reduced",
      "Conversion increased",
      "Biometric precision",
      "Concurrent users",
    ],
    demoTag: "DEMO",
    demoTitle: "Request an enterprise demo",
    demoLead:
      "Tell us about your catalog, business goals and team. We will come back with a demo plan tailored to your retail environment.",
    demoFields: {
      name: "Name",
      company: "Company",
      email: "Professional email",
      role: "Role",
      catalog: "Catalog size",
      message: "Message",
    },
    catalogOptions: ["<1000", "1000-10000", "10000-50000", "50000+"],
    trustTitle: "Why retailers trust us",
    trustCards: [
      {
        title: "Patented technology",
        body: "PCT/EP2025/067317",
      },
      {
        title: "GDPR compliant",
        body: "Encrypted and ephemeral biometric data",
      },
      {
        title: "Pilots underway",
        body: "With leading European retailers",
      },
      {
        title: "Measurable ROI",
        body: "Return reduction proven from month one",
      },
    ],
    pauTag: "P.A.U.",
    pauTitle: "Your AI fitting assistant that guides customers through the try-on experience",
    pauLead:
      "P.A.U. supports each step of the journey to make virtual try-on clearer, faster and more reassuring before purchase.",
    pauBody:
      "Built for fashion retail, P.A.U. helps capture the right inputs, explain the result and accelerate purchase decisions with less friction.",
    pauCapabilityTitle: "What P.A.U. orchestrates",
    pauCapabilities: [
      "Customer guidance during scan",
      "Assistance during fit simulation",
      "Purchase confidence before checkout",
    ],
    pauLiveLabel: "Live status",
    pauSnapCta: "Launch the demo",
    pauStatusReady: "P.A.U. is authorised and ready to operate.",
    pauStatusLocked: "P.A.U. is waiting for an authorised node or an active UserCheck.",
    manifestoIntro:
      "A founding vision, now distilled to what matters most: replacing size uncertainty with fit certainty retailers can use.",
    manifestoQuoteLabel: "Vision",
    footerDescription: "AI-powered virtual try-on for fashion retail",
    footerPrivacyLabel: "Privacy Policy",
    footerTermsLabel: "Terms",
  },
  es: {
    navLinks: [
      { label: "Tecnología", href: "#technology" },
      { label: "Solución", href: "#solution" },
      { label: "Demo", href: "#demo" },
      { label: "Contacto", href: "#contact" },
    ],
    navCta: "Solicitar una demo",
    heroHeadline: "Reduce devoluciones en moda un 85% con IA que predice el fit perfecto",
    heroSubheadline:
      "TryOnYou crea un gemelo digital de cada cliente para simular el ajuste real de las prendas — antes de la compra.",
    heroTrust:
      "Pilotos en curso con retailers europeos · Tecnología patentada · RGPD compliant",
    problemTitle: "El problema",
    problemBody:
      "Las devoluciones en e-commerce moda cuestan 550.000M€/año. El 52% son por mal ajuste. Cada devolución erosiona el margen y la confianza del cliente.",
    solutionTitle: "La solución",
    solutionBody:
      "Un gemelo digital del cliente + simulación textil IA = certeza de ajuste antes de la compra. Cero talla clásica, cero fricción.",
    resultTitle: "El resultado",
    resultBody: "-85% devoluciones · +25% conversión · 99,7% precisión biométrica",
    howItWorksTag: "CÓMO FUNCIONA",
    howItWorksTitle: "Simple para el cliente, medible para el retailer",
    howItWorksSteps: [
      "El cliente se coloca frente al espejo o cámara",
      "Nuestra IA crea un gemelo digital y simula las prendas en tiempo real",
      "El cliente ve el resultado, elige y compra con certeza",
    ],
    technologyTag: "TECNOLOGÍA",
    technologyTitle: "IA de simulación textil, no un filtro de foto",
    technologyLead:
      "TryOnYou combina gemelo digital, biometría y simulación textil para predecir el ajuste real antes de la compra.",
    technologyNarrative:
      "Pensado para reducir devoluciones, elevar conversión y soportar despliegues retail a escala enterprise.",
    metricLabels: [
      "Devoluciones reducidas",
      "Conversión aumentada",
      "Precisión biométrica",
      "Usuarios concurrentes",
    ],
    demoTag: "DEMO",
    demoTitle: "Solicita una demo enterprise",
    demoLead:
      "Cuéntanos tu catálogo, tus objetivos y tu equipo. Volveremos con un plan de demo adaptado a tu operación retail.",
    demoFields: {
      name: "Nombre",
      company: "Empresa",
      email: "Email profesional",
      role: "Cargo",
      catalog: "Tamaño del catálogo",
      message: "Mensaje",
    },
    catalogOptions: ["<1000", "1000-10000", "10000-50000", "50000+"],
    trustTitle: "Por qué los retailers confían en nosotros",
    trustCards: [
      {
        title: "Tecnología patentada",
        body: "PCT/EP2025/067317",
      },
      {
        title: "RGPD compliant",
        body: "Datos biométricos cifrados y efímeros",
      },
      {
        title: "Pilotos en curso",
        body: "Con retailers europeos de primer nivel",
      },
      {
        title: "ROI medible",
        body: "Reducción de devoluciones probada desde el primer mes",
      },
    ],
    pauTag: "P.A.U.",
    pauTitle: "Your AI fitting assistant that guides customers through the try-on experience",
    pauLead:
      "P.A.U. acompaña cada paso para hacer la prueba virtual más clara, rápida y confiable antes de comprar.",
    pauBody:
      "Diseñado para retail moda, P.A.U. ayuda a capturar los datos necesarios, explicar el resultado y acelerar la decisión de compra con menos fricción.",
    pauCapabilityTitle: "Qué orquesta P.A.U.",
    pauCapabilities: [
      "Guía al cliente durante el escaneo",
      "Asistencia durante la simulación del fit",
      "Certeza antes del checkout",
    ],
    pauLiveLabel: "Estado en vivo",
    pauSnapCta: "Lanzar la demo",
    pauStatusReady: "P.A.U. autorizado y listo para operar.",
    pauStatusLocked: "P.A.U. espera un nodo autorizado o un UserCheck activo.",
    manifestoIntro:
      "Una visión fundacional, ahora llevada a lo esencial: sustituir la incertidumbre de talla por certeza de fit utilizable para retail.",
    manifestoQuoteLabel: "Visión",
    footerDescription: "Virtual try-on con IA para retail moda",
    footerPrivacyLabel: "Privacy Policy",
    footerTermsLabel: "Terms",
  },
};

const lafayetteCollection = lafayetteCollectionRaw as LafayetteGarment[];

const AMBIENT_PARTICLES = Array.from({ length: 18 }, (_, index) => ({
  id: `ambient-particle-${index}`,
  left: `${4 + ((index * 5.2) % 92)}%`,
  size: `${2 + (index % 3)}px`,
  opacity: 0.12 + (index % 5) * 0.06,
  delay: `${(index % 6) * 1.15}s`,
  duration: `${12 + (index % 5) * 2.8}s`,
  drift: `${index % 2 === 0 ? 16 + (index % 4) * 6 : -14 - (index % 4) * 7}px`,
}));

function useScrollReveal<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || visible) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.15) {
          setVisible(true);
          observer.disconnect();
        }
      },
      {
        threshold: [0, 0.15, 0.3, 0.5],
      },
    );

    observer.observe(node);

    return () => observer.disconnect();
  }, [visible]);

  return { ref, visible };
}

type AnimatedMetricProps = {
  value: number;
  label: string;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  visible: boolean;
};

function AnimatedMetric({
  value,
  label,
  prefix = "",
  suffix = "",
  decimals = 0,
  visible,
}: AnimatedMetricProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (!visible) return;

    let frame = 0;
    const duration = 1500;
    const startedAt = performance.now();
    const easeOutCubic = (progress: number) => 1 - Math.pow(1 - progress, 3);

    const animate = (now: number) => {
      const progress = Math.min((now - startedAt) / duration, 1);
      const eased = easeOutCubic(progress);
      setDisplayValue(value * eased);

      if (progress < 1) {
        frame = window.requestAnimationFrame(animate);
      }
    };

    setDisplayValue(0);
    frame = window.requestAnimationFrame(animate);

    return () => window.cancelAnimationFrame(frame);
  }, [value, visible]);

  const formattedValue = decimals > 0 ? displayValue.toFixed(decimals) : String(Math.round(displayValue));

  return (
    <article className="metric-card">
      <strong>
        {prefix}
        {formattedValue}
        {suffix}
      </strong>
      <span>{label}</span>
    </article>
  );
}

type DemoFormState = {
  name: string;
  company: string;
  email: string;
  role: string;
  catalogSize: string;
  message: string;
};

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
  const [navScrolled, setNavScrolled] = useState(false);
  const [demoForm, setDemoForm] = useState<DemoFormState>({
    name: "",
    company: "",
    email: "",
    role: "",
    catalogSize: "",
    message: "",
  });
  const [demoStatus, setDemoStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");

  const heroSectionRef = useRef<HTMLElement | null>(null);
  const heroReveal = useScrollReveal<HTMLElement>();
  const solutionReveal = useScrollReveal<HTMLElement>();
  const technologyReveal = useScrollReveal<HTMLElement>();
  const demoReveal = useScrollReveal<HTMLElement>();
  const trustReveal = useScrollReveal<HTMLElement>();
  const pauReveal = useScrollReveal<HTMLElement>();
  const manifestoReveal = useScrollReveal<HTMLElement>();

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
  const pageCopy = LANDING_CONTENT[locale];

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
    openInaugurationStripeLiquidity();
  };

  const handlePricingAction = (action: "pilot" | "pro" | "enterprise") => {
    if (action === "pilot") {
      void onHeroSubmit();
      return;
    }
    if (action === "pro") {
      onInaugurationStripeCharge();
      return;
    }
    onLafayetteStripeCharge();
  };

  const pauDistrictLabel =
    activeDistrict === "75004"
      ? "BHV Marais · 75004"
      : activeDistrict === "75009"
        ? "Galeries Lafayette · 75009"
        : "Paris pilot";

  const scrollToSelector = (selector: string) => {
    const target = document.querySelector<HTMLElement>(selector);
    if (!target) return;
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    window.history.replaceState(null, "", selector);
  };

  const handleAnchorClick = (
    event: MouseEvent<HTMLAnchorElement>,
    href: string,
  ) => {
    if (!href.startsWith("#")) return;
    const target = document.querySelector<HTMLElement>(href);
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    window.history.replaceState(null, "", href);
  };

  const heroMetrics = [
    { value: 85, prefix: "-", suffix: "%", label: pageCopy.metricLabels[0] },
    { value: 25, prefix: "+", suffix: "%", label: pageCopy.metricLabels[1] },
    { value: 99.7, suffix: "%", decimals: 1, label: pageCopy.metricLabels[2] },
    { value: 10, suffix: "K", label: pageCopy.metricLabels[3] },
  ] as const;

  const bindHeroSection = (node: HTMLElement | null) => {
    heroSectionRef.current = node;
    heroReveal.ref.current = node;
  };

  useEffect(() => {
    const updateNavbarState = () => {
      const heroHeight = heroSectionRef.current?.offsetHeight ?? window.innerHeight * 0.8;
      setNavScrolled(window.scrollY > heroHeight * 0.35);
    };

    updateNavbarState();
    window.addEventListener("scroll", updateNavbarState, { passive: true });
    window.addEventListener("resize", updateNavbarState);

    return () => {
      window.removeEventListener("scroll", updateNavbarState);
      window.removeEventListener("resize", updateNavbarState);
    };
  }, []);

  const handleDemoInput = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target;
    setDemoForm((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleDemoSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setDemoStatus("submitting");

    try {
      const response = await fetch("/api/demo-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: demoForm.name.trim(),
          company: demoForm.company.trim(),
          email: demoForm.email.trim(),
          role: demoForm.role.trim(),
          catalog_size: demoForm.catalogSize.trim() || undefined,
          message: demoForm.message.trim() || undefined,
          source: "landing_demo_form",
          locale,
          ts: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        throw new Error("demo-request-failed");
      }

      setDemoStatus("success");
      setDemoForm({
        name: "",
        company: "",
        email: "",
        role: "",
        catalogSize: "",
        message: "",
      });
    } catch {
      setDemoStatus("error");
    }
  };

  return (
    <div
      className="app-root"
      style={{
        background:
          "radial-gradient(circle at top, rgba(212,175,55,0.08), transparent 24%), linear-gradient(165deg, #0c0d10 0%, #141619 40%, #1a1b20 70%, #0c0d10 100%)",
        color: "#f5efe6",
      }}
    >
      <div className="app-stage" aria-hidden>
        <div className="app-stage__particles">
          {AMBIENT_PARTICLES.map((particle) => (
            <span
              key={particle.id}
              className="ambient-particle"
              style={{
                left: particle.left,
                width: particle.size,
                height: particle.size,
                opacity: particle.opacity,
                animationDelay: particle.delay,
                animationDuration: particle.duration,
                ["--particle-drift" as const]: particle.drift,
              }}
            />
          ))}
        </div>
      </div>

      <div className="app-ui">
        <header className="site-nav" data-scrolled={navScrolled ? "1" : undefined}>
          <div className="site-nav__inner">
            <a
              className="site-nav__brand"
              href="#hero"
              aria-label="TryOnYou home"
              onClick={(event) => handleAnchorClick(event, "#hero")}
            >
              <span className="site-nav__monogram">TY</span>
              <span>
                <strong>TRYONYOU</strong>
              </span>
            </a>

            <nav className="site-nav__links" aria-label="Primary">
              {pageCopy.navLinks.map((item) => (
                <a key={item.href} href={item.href} onClick={(event) => handleAnchorClick(event, item.href)}>
                  {item.label}
                </a>
              ))}
            </nav>

            <div className="site-nav__actions">
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

              <button type="button" className="btn-primary site-nav__cta" onClick={() => scrollToSelector("#demo")}>
                {pageCopy.navCta}
              </button>
            </div>
          </div>
        </header>

        <main className="landing-main">
          <section
            id="hero"
            ref={bindHeroSection}
            className="landing-section hero-section"
            data-visible={heroReveal.visible ? "1" : undefined}
          >
            <motion.div
              className="hero-card"
              initial={{ opacity: 0, y: 26 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, ease: "easeOut" }}
            >
              <h1 className="hero-title">{pageCopy.heroHeadline}</h1>
              <p className="hero-lead">{pageCopy.heroSubheadline}</p>
              <button type="button" className="btn-primary btn-primary--hero" onClick={() => scrollToSelector("#demo")}>
                {pageCopy.navCta}
              </button>
              <p className="hero-trust-line">{pageCopy.heroTrust}</p>
            </motion.div>
          </section>

          <section
            id="solution"
            ref={solutionReveal.ref}
            className="landing-section solution-section"
            data-visible={solutionReveal.visible ? "1" : undefined}
          >
            <div className="psr-grid">
              <article className="info-card info-card--problem">
                <span className="info-card__eyebrow">01</span>
                <h2>{pageCopy.problemTitle}</h2>
                <p>{pageCopy.problemBody}</p>
              </article>
              <article className="info-card info-card--solution">
                <span className="info-card__eyebrow">02</span>
                <h2>{pageCopy.solutionTitle}</h2>
                <p>{pageCopy.solutionBody}</p>
              </article>
              <article className="info-card info-card--result">
                <span className="info-card__eyebrow">03</span>
                <h2>{pageCopy.resultTitle}</h2>
                <p>{pageCopy.resultBody}</p>
              </article>
            </div>

            <div className="how-it-works-card">
              <div className="section-heading section-heading--centered">
                <p className="section-tag">{pageCopy.howItWorksTag}</p>
                <h2>{pageCopy.howItWorksTitle}</h2>
              </div>

              <div className="steps-grid">
                {pageCopy.howItWorksSteps.map((step, index) => (
                  <article key={step} className="step-card">
                    <span className="step-card__number">0{index + 1}</span>
                    <p>{step}</p>
                  </article>
                ))}
              </div>

              <div className="section-cta-center">
                <button type="button" className="btn-primary" onClick={() => scrollToSelector("#demo")}>
                  {pageCopy.navCta}
                </button>
              </div>
            </div>
          </section>

          <section
            id="technology"
            ref={technologyReveal.ref}
            className="landing-section technology-section"
            data-visible={technologyReveal.visible ? "1" : undefined}
          >
            <div className="section-heading">
              <p className="section-tag">{pageCopy.technologyTag}</p>
              <h2>{pageCopy.technologyTitle}</h2>
              <p>{pageCopy.technologyLead}</p>
            </div>

            <div className="technology-layout">
              <div className="technology-video-card">
                <video autoPlay loop muted playsInline>
                  <source src="/assets/videos/inauguration_theatre.mp4" type="video/mp4" />
                </video>
                <div className="technology-video-card__caption">
                  <strong>ZERO-SIZE PROTOCOL</strong>
                  <span>{pageCopy.technologyNarrative}</span>
                </div>
              </div>

              <div className="metrics-grid">
                {heroMetrics.map((metric) => (
                  <AnimatedMetric
                    key={metric.label}
                    value={metric.value}
                    label={metric.label}
                    prefix={metric.prefix}
                    suffix={metric.suffix}
                    decimals={metric.decimals}
                    visible={technologyReveal.visible}
                  />
                ))}
              </div>
            </div>
          </section>

          <section
            id="demo"
            ref={demoReveal.ref}
            className="landing-section demo-section"
            data-visible={demoReveal.visible ? "1" : undefined}
          >
            <div className="demo-layout">
              <div className="section-heading">
                <p className="section-tag">{pageCopy.demoTag}</p>
                <h2>{pageCopy.demoTitle}</h2>
                <p>{pageCopy.demoLead}</p>
              </div>

              <form className="demo-form-card" onSubmit={handleDemoSubmit}>
                <div className="demo-form-grid">
                  <label className="form-field">
                    <span>{pageCopy.demoFields.name}</span>
                    <input
                      type="text"
                      name="name"
                      value={demoForm.name}
                      onChange={handleDemoInput}
                      required
                    />
                  </label>

                  <label className="form-field">
                    <span>{pageCopy.demoFields.company}</span>
                    <input
                      type="text"
                      name="company"
                      value={demoForm.company}
                      onChange={handleDemoInput}
                      required
                    />
                  </label>

                  <label className="form-field">
                    <span>{pageCopy.demoFields.email}</span>
                    <input
                      type="email"
                      name="email"
                      value={demoForm.email}
                      onChange={handleDemoInput}
                      required
                    />
                  </label>

                  <label className="form-field">
                    <span>{pageCopy.demoFields.role}</span>
                    <input
                      type="text"
                      name="role"
                      value={demoForm.role}
                      onChange={handleDemoInput}
                      required
                    />
                  </label>

                  <label className="form-field">
                    <span>{pageCopy.demoFields.catalog}</span>
                    <select
                      name="catalogSize"
                      value={demoForm.catalogSize}
                      onChange={handleDemoInput}
                    >
                      <option value="">{copy.demoFormCatalogPlaceholder}</option>
                      {pageCopy.catalogOptions.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="form-field form-field--full">
                    <span>{pageCopy.demoFields.message}</span>
                    <textarea
                      name="message"
                      value={demoForm.message}
                      onChange={handleDemoInput}
                      rows={5}
                    />
                  </label>
                </div>

                <div className="demo-form-footer">
                  <button type="submit" className="btn-primary btn-primary--full" disabled={demoStatus === "submitting"}>
                    {demoStatus === "submitting" ? copy.demoFormSubmitting : pageCopy.navCta}
                  </button>

                  {demoStatus === "success" ? (
                    <div className="demo-form-message demo-form-message--success" role="status">
                      <strong>{copy.demoFormSuccessTitle}</strong>
                      <p>{copy.demoFormSuccessBody}</p>
                    </div>
                  ) : null}

                  {demoStatus === "error" ? (
                    <div className="demo-form-message demo-form-message--error" role="alert">
                      <strong>{copy.demoFormError}</strong>
                      <p>{copy.demoFormRetry}</p>
                    </div>
                  ) : null}
                </div>
              </form>
            </div>
          </section>

          <section
            id="trust"
            ref={trustReveal.ref}
            className="landing-section trust-section"
            data-visible={trustReveal.visible ? "1" : undefined}
          >
            <div className="section-heading section-heading--centered">
              <h2>{pageCopy.trustTitle}</h2>
            </div>

            <div className="trust-grid">
              {pageCopy.trustCards.map((card, index) => (
                <motion.article
                  key={card.title}
                  className="trust-card"
                  initial={{ opacity: 0, y: 24 }}
                  animate={trustReveal.visible ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.45, delay: index * 0.08 }}
                >
                  <h3>{card.title}</h3>
                  <p>{card.body}</p>
                </motion.article>
              ))}
            </div>

            <div className="section-cta-center">
              <button type="button" className="btn-primary" onClick={() => scrollToSelector("#demo")}>
                {pageCopy.navCta}
              </button>
            </div>
          </section>

          <section
            id="pau"
            ref={pauReveal.ref}
            className="landing-section pau-section"
            data-visible={pauReveal.visible ? "1" : undefined}
          >
            <div className="pau-layout">
              <div className="pau-visual-card">
                <p className="section-tag">{pageCopy.pauTag}</p>
                <button
                  type="button"
                  className={
                    isMaraisNode && pauStarted ? "app-pau app-pau--marais pau-section__orb" : "app-pau app-pau--lafayette pau-section__orb"
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

                <div className="pau-visual-card__status">
                  <span>{pageCopy.pauLiveLabel}</span>
                  <strong>{pauStarted ? pageCopy.pauStatusReady : pageCopy.pauStatusLocked}</strong>
                  <p>{pauDistrictLabel}</p>
                </div>
              </div>

              <div className="pau-copy-card">
                <h2>{pageCopy.pauTitle}</h2>
                <p className="pau-copy-card__lead">{pageCopy.pauLead}</p>
                <p>{pageCopy.pauBody}</p>

                <div className="pau-script-card">
                  <h3>{pageCopy.pauCapabilityTitle}</h3>
                  <ul>
                    {pageCopy.pauCapabilities.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="pau-message-stack">
                  {[copy.pauGuideGreeting, copy.pauGuideScan, copy.pauGuideSnap, copy.pauGuideNext].map((line) => (
                    <div key={line} className="pau-message-bubble">
                      {line}
                    </div>
                  ))}
                </div>

                <div className="pau-cta-row">
                  <button type="button" className="btn-primary" onClick={theSnap} disabled={!pauStarted}>
                    {pageCopy.pauSnapCta}
                  </button>
                  <button type="button" className="btn-secondary" onClick={() => scrollToSelector("#demo")}>
                    {pageCopy.navCta}
                  </button>
                </div>
                <p className="pau-copy-card__meta">{julesLane}</p>
              </div>
            </div>
          </section>

          <section
            id="manifesto"
            ref={manifestoReveal.ref}
            className="landing-section manifesto-section manifesto-section--subtle"
            data-visible={manifestoReveal.visible ? "1" : undefined}
          >
            <div className="section-heading section-heading--centered">
              <p className="section-tag">{copy.manifestoTag}</p>
              <h2>{copy.manifestoTitle}</h2>
              <p>{pageCopy.manifestoIntro}</p>
            </div>

            <div className="manifesto-grid manifesto-grid--compact">
              <article className="manifesto-panel manifesto-panel--lead">
                <span className="manifesto-panel__label">{pageCopy.manifestoQuoteLabel}</span>
                <blockquote>{copy.manifestoBody}</blockquote>
              </article>
              <article className="manifesto-panel">
                <p>{copy.manifestoAccumulation}</p>
              </article>
              <article className="manifesto-panel">
                <p>{copy.manifestoColor}</p>
              </article>
              <article className="manifesto-panel manifesto-panel--accent">
                <p>{copy.manifestoIdentity}</p>
              </article>
            </div>

            <div className="manifesto-slogan-wrap">
              <p className="manifesto-cta">{copy.manifestoCta}</p>
              <p className="manifesto-slogan">{copy.manifestoSlogan}</p>
              <div className="manifesto-meta">
                <span>{copy.manifestoHashtags}</span>
                <span>{copy.manifestoLafayette}</span>
              </div>
            </div>
          </section>
        </main>

        <OfrendaOverlay
          elasticLabel={elasticLabel}
          julesLane={julesLane}
          onOfrenda={onOfrenda}
          locale={locale}
          headerExtra={
            <button
              type="button"
              onClick={() => scrollToSelector("#demo")}
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
              {pageCopy.navCta}
            </button>
          }
        />

        <footer id="contact" className="app-footer">
          <div className="app-footer__top">
            <div>
              <strong>TRYONYOU</strong>
              <p>{pageCopy.footerDescription}</p>
              <p className="app-footer__tagline">PA, PA, PA. LET'S BE THE TENDENCY.</p>
            </div>
            <div className="app-footer__links">
              <a href="mailto:info@tryonyou.app">info@tryonyou.app</a>
              <a href="https://www.linkedin.com/company/tryonyou" target="_blank" rel="noopener noreferrer">
                LinkedIn
              </a>
              <a href="/privacy-policy">{pageCopy.footerPrivacyLabel}</a>
              <a href="/terms">{pageCopy.footerTermsLabel}</a>
            </div>
          </div>
          <div className="app-legal">
            SIRET 94361019600017 · PCT/EP2025/067317
          </div>
        </footer>
      </div>

      <PreScanHook
        visible={preScanVisible}
        onDismiss={() => {
          sessionStorage.setItem("tryonyou_prescan_done", "1");
          setPreScanVisible(false);
        }}
      />
      <PauFloatingGuide locale={locale} />
    </div>
  );
}
