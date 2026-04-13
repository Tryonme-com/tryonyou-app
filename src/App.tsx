import {
  type ChangeEvent,
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
  heroMeta: string;
  heroPanelLabel: string;
  heroPanelTitle: string;
  heroPanelBody: string;
  heroSecondaryCta: string;
  heroContractKicker: string;
  heroContractBody: string;
  manifestoIntro: string;
  manifestoQuoteLabel: string;
  technologyTag: string;
  technologyTitle: string;
  technologyLead: string;
  technologyNarrative: string;
  metricLabels: readonly string[];
  collectionTag: string;
  collectionTitle: string;
  collectionLead: string;
  collectionPrecisionLabel: string;
  collectionFabricLabel: string;
  collectionProfilesLabel: string;
  patentTag: string;
  patentTitle: string;
  patentBody: string;
  contractTag: string;
  contractTitle: string;
  contractBody: string;
  contractLabels: readonly string[];
  pricingTag: string;
  pricingTitle: string;
  pricingLead: string;
  pricingCards: readonly {
    title: string;
    price: string;
    badge: string;
    description: string;
    features: readonly string[];
    cta: string;
    action: "pilot" | "pro" | "enterprise";
    highlight?: boolean;
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
  footerLine: string;
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
      { label: "Manifeste", href: "#manifesto" },
      { label: "Technologie", href: "#technology" },
      { label: "Collection", href: "#collection" },
      { label: "Tarifs", href: "#pricing" },
      { label: "P.A.U.", href: "#pau" },
    ],
    heroMeta: "Paris · Galeries Lafayette · Maison Digitale",
    heroPanelLabel: "Lancement 2026",
    heroPanelTitle: "La mode sans friction, avec certitude souveraine.",
    heroPanelBody:
      "Une expérience premium pensée pour la vente assistée, l’essayage sans tailles classiques et l’activation immédiate des maisons de luxe en boutique.",
    heroSecondaryCta: "Rejoindre la bêta privée",
    heroContractKicker: "Cadre commercial actif",
    heroContractBody: "Pilotage boutique, activation inauguration, orchestration P.A.U. et lien de paiement live prêts pour la conversion.",
    manifestoIntro: "La vision fondatrice de Rubén, pensée comme un cri de guerre pour Paris 2026.",
    manifestoQuoteLabel: "War cry",
    technologyTag: "LA PREUVE OPÉRATIONNELLE",
    technologyTitle: "The 0sizes Era commence dans le théâtre de vente.",
    technologyLead:
      "TryOnYou transforme l’essayage en un moment éditorial, mesurable et immédiatement monétisable pour les maisons, les corners premium et les investisseurs retail-tech.",
    technologyNarrative:
      "Du miroir biométrique à la logistique hôtel-boutique, chaque interaction réduit le retour, augmente la conversion et maintient la désirabilité intacte.",
    metricLabels: [
      "Retours éliminés",
      "Conversion ventes",
      "Précision biométrique",
      "Utilisateurs simultanés",
    ],
    collectionTag: "APERÇU CURATÉ",
    collectionTitle: "Une garde-robe Lafayette, sélectionnée pour la démonstration premium.",
    collectionLead:
      "Huit pièces iconiques montrent comment Divineo met en scène la matière, la couleur et la précision de coupe sans exposer la taille.",
    collectionPrecisionLabel: "Précision",
    collectionFabricLabel: "Matière",
    collectionProfilesLabel: "Profil d’ajustage",
    patentTag: "PROPRIÉTÉ INTELLECTUELLE",
    patentTitle: "Un actif protégé, lisible pour le marché et défendable pour l’investisseur.",
    patentBody:
      "Brevet international PCT/EP2025/067317. Huit super-claims. The Snap™, génération adaptative d’avatars, orchestration boutique et signalement de valeur opérationnelle déjà intégrés dans l’expérience commerciale.",
    contractTag: "CADRE LAFAYETTE",
    contractTitle: "Une proposition de licence claire, premium et immédiatement négociable.",
    contractBody:
      "Le dispositif financier combine activation, exclusivité territoriale et royalties pour rendre la décision simple côté retail tout en préservant la marge haute valeur de TryOnYou.",
    contractLabels: [
      "Setup fee",
      "Exclusivité territoriale",
      "Royalties sur ventes",
      "Total immédiat",
    ],
    pricingTag: "OFFRE COMMERCIALE",
    pricingTitle: "Trois portes d’entrée, une même signature de luxe digital.",
    pricingLead:
      "De la validation terrain au déploiement multi-site, la structure tarifaire conserve la désirabilité du produit tout en facilitant l’adoption B2B.",
    pricingCards: [
      {
        title: "Pilote Gratuit",
        price: "1 mois offert",
        badge: "Découverte",
        description: "Un mois pour prouver le taux de conversion, affiner le rituel d’essayage et former les équipes boutique.",
        features: [
          "1 miroir Divineo en test",
          "Support onboarding maison",
          "Mesures conversion & retour",
        ],
        cta: "Activer le pilote",
        action: "pilot",
      },
      {
        title: "Divineo Pro",
        price: "299€/mo",
        badge: "Recommandé",
        description: "Le format parfait pour un corner premium qui veut vendre plus sans surcharger l’espace ni l’expérience client.",
        features: [
          "Assistant P.A.U. orchestré",
          "Checkout souverain en EUR",
          "Support commercial prioritaire",
        ],
        cta: "Parler au commercial",
        action: "pro",
        highlight: true,
      },
      {
        title: "Divineo Enterprise",
        price: "Sur mesure",
        badge: "Maison & groupe",
        description: "Pour les réseaux luxe, les grands magasins et les déploiements internationaux avec gouvernance sur mesure.",
        features: [
          "Déploiement multi-sites",
          "Intégration CRM / data room",
          "Conditions exclusives investisseurs",
        ],
        cta: "Ouvrir un mandat",
        action: "enterprise",
      },
    ],
    pauTag: "ASSISTANT MAISON",
    pauTitle: "P.A.U., la présence digitale qui guide, rassure et déclenche l’achat.",
    pauLead:
      "Pensé comme un concierge couture dopé à l’IA, P.A.U. traduit la biométrie en langage désir, puis pousse l’essayage vers le moment décisif: The Snap.",
    pauBody:
      "Le guide accompagne la cliente, structure le rituel et transforme l’instant d’hésitation en certitude souveraine sans jamais rompre l’esthétique maison.",
    pauCapabilityTitle: "Rituel guidé",
    pauCapabilities: [
      "Accueil et préparation émotionnelle",
      "Scan silhouette avec précision biométrique",
      "Révélation instantanée d’un nouveau look",
    ],
    pauLiveLabel: "Statut live",
    pauSnapCta: "Déclencher The Snap",
    pauStatusReady: "P.A.U. autorisé et prêt à opérer.",
    pauStatusLocked: "P.A.U. attend un nœud autorisé ou un UserCheck actif.",
    footerLine: "Contact maison: info@tryonyou.app · Paris · Galeries Lafayette · Investor-ready experience",
  },
  en: {
    navLinks: [
      { label: "Manifesto", href: "#manifesto" },
      { label: "Technology", href: "#technology" },
      { label: "Collection", href: "#collection" },
      { label: "Pricing", href: "#pricing" },
      { label: "P.A.U.", href: "#pau" },
    ],
    heroMeta: "Paris · Galeries Lafayette · Digital Maison",
    heroPanelLabel: "2026 launch",
    heroPanelTitle: "Frictionless fashion with sovereign fit certainty.",
    heroPanelBody:
      "A premium experience designed for assisted selling, hanger-free fitting and immediate activation for luxury maisons in-store.",
    heroSecondaryCta: "Join the private beta",
    heroContractKicker: "Commercial framework live",
    heroContractBody: "Boutique pilot, inauguration activation, P.A.U. orchestration and live payment links are ready for conversion.",
    manifestoIntro: "Rubén’s founding vision, written as a war cry for Paris 2026.",
    manifestoQuoteLabel: "War cry",
    technologyTag: "OPERATIONAL PROOF",
    technologyTitle: "The 0sizes Era begins inside the selling theatre.",
    technologyLead:
      "TryOnYou turns fitting into an editorial, measurable and instantly monetisable moment for maisons, premium corners and retail-tech investors.",
    technologyNarrative:
      "From biometric mirror to hotel-boutique logistics, every interaction cuts returns, lifts conversion and preserves desirability.",
    metricLabels: [
      "Returns reduced",
      "Sales conversion",
      "Biometric precision",
      "Concurrent users",
    ],
    collectionTag: "CURATED PREVIEW",
    collectionTitle: "A Lafayette wardrobe selected for premium demonstration.",
    collectionLead:
      "Eight iconic pieces show how Divineo stages fabric, colour and precision tailoring without exposing size.",
    collectionPrecisionLabel: "Precision",
    collectionFabricLabel: "Fabric",
    collectionProfilesLabel: "Fit profile",
    patentTag: "INTELLECTUAL PROPERTY",
    patentTitle: "A protected asset that is market-readable and investor-defensible.",
    patentBody:
      "International patent PCT/EP2025/067317. Eight super-claims. The Snap™, adaptive avatar generation, in-store orchestration and operational value signalling are already integrated into the commercial experience.",
    contractTag: "LAFAYETTE FRAMEWORK",
    contractTitle: "A licensing proposal that is clear, premium and immediately negotiable.",
    contractBody:
      "The financial setup combines activation, territorial exclusivity and royalties to simplify retail decision-making while preserving TryOnYou’s high-value margin.",
    contractLabels: [
      "Setup fee",
      "Territorial exclusivity",
      "Sales royalties",
      "Immediate total",
    ],
    pricingTag: "COMMERCIAL OFFER",
    pricingTitle: "Three entry points, one luxury digital signature.",
    pricingLead:
      "From field validation to multi-site deployment, pricing preserves product desirability while making B2B adoption easier.",
    pricingCards: [
      {
        title: "Pilote Gratuit",
        price: "1 month free",
        badge: "Discovery",
        description: "One month to prove conversion uplift, refine the fitting ritual and train boutique teams.",
        features: [
          "1 Divineo mirror in test mode",
          "Maison onboarding support",
          "Conversion & return metrics",
        ],
        cta: "Activate pilot",
        action: "pilot",
      },
      {
        title: "Divineo Pro",
        price: "299€/mo",
        badge: "Recommended",
        description: "The ideal format for a premium corner that wants to sell more without cluttering space or experience.",
        features: [
          "Orchestrated P.A.U. assistant",
          "Sovereign checkout in EUR",
          "Priority commercial support",
        ],
        cta: "Talk to sales",
        action: "pro",
        highlight: true,
      },
      {
        title: "Divineo Enterprise",
        price: "Custom",
        badge: "Maison & group",
        description: "For luxury networks, department stores and international rollouts with bespoke governance.",
        features: [
          "Multi-site deployment",
          "CRM / data room integration",
          "Exclusive investor terms",
        ],
        cta: "Open mandate",
        action: "enterprise",
      },
    ],
    pauTag: "MAISON ASSISTANT",
    pauTitle: "P.A.U., the digital presence that guides, reassures and closes the sale.",
    pauLead:
      "Designed like an AI couture concierge, P.A.U. translates biometrics into desire and drives fitting toward the decisive moment: The Snap.",
    pauBody:
      "The guide accompanies the client, structures the ritual and turns hesitation into sovereign certainty without ever breaking the maison aesthetic.",
    pauCapabilityTitle: "Guided ritual",
    pauCapabilities: [
      "Welcome and emotional priming",
      "Silhouette scan with biometric precision",
      "Instant reveal of a new look",
    ],
    pauLiveLabel: "Live status",
    pauSnapCta: "Trigger The Snap",
    pauStatusReady: "P.A.U. is authorised and ready to operate.",
    pauStatusLocked: "P.A.U. is waiting for an authorised node or an active UserCheck.",
    footerLine: "Maison contact: info@tryonyou.app · Paris · Galeries Lafayette · Investor-ready experience",
  },
  es: {
    navLinks: [
      { label: "Manifiesto", href: "#manifesto" },
      { label: "Tecnología", href: "#technology" },
      { label: "Colección", href: "#collection" },
      { label: "Precios", href: "#pricing" },
      { label: "P.A.U.", href: "#pau" },
    ],
    heroMeta: "París · Galeries Lafayette · Maison Digitale",
    heroPanelLabel: "Lanzamiento 2026",
    heroPanelTitle: "Moda sin fricción con certeza soberana de ajuste.",
    heroPanelBody:
      "Una experiencia premium pensada para venta asistida, prueba sin perchas ni tallas clásicas y activación inmediata para casas de lujo en tienda.",
    heroSecondaryCta: "Unirme a la beta privada",
    heroContractKicker: "Marco comercial activo",
    heroContractBody: "Piloto boutique, activación inaugural, orquestación P.A.U. y enlaces de pago live listos para convertir.",
    manifestoIntro: "La visión fundacional de Rubén, escrita como un grito de guerra para París 2026.",
    manifestoQuoteLabel: "War cry",
    technologyTag: "PRUEBA OPERATIVA",
    technologyTitle: "La era 0sizes empieza dentro del teatro de venta.",
    technologyLead:
      "TryOnYou convierte la prueba en un momento editorial, medible y monetizable al instante para maisons, corners premium e inversores retail-tech.",
    technologyNarrative:
      "Del espejo biométrico a la logística hotel-boutique, cada interacción reduce devoluciones, eleva la conversión y mantiene intacto el deseo.",
    metricLabels: [
      "Devoluciones reducidas",
      "Conversión de ventas",
      "Precisión biométrica",
      "Usuarios simultáneos",
    ],
    collectionTag: "SELECCIÓN CURADA",
    collectionTitle: "Un armario Lafayette seleccionado para una demostración premium.",
    collectionLead:
      "Ocho piezas icónicas muestran cómo Divineo pone en escena tejido, color y precisión de patronaje sin exponer la talla.",
    collectionPrecisionLabel: "Precisión",
    collectionFabricLabel: "Tejido",
    collectionProfilesLabel: "Perfil de ajuste",
    patentTag: "PROPIEDAD INTELECTUAL",
    patentTitle: "Un activo protegido, legible para el mercado y defendible para el inversor.",
    patentBody:
      "Patente internacional PCT/EP2025/067317. Ocho super-claims. The Snap™, generación adaptativa de avatares, orquestación boutique y señal operativa de valor ya integrados en la experiencia comercial.",
    contractTag: "MARCO LAFAYETTE",
    contractTitle: "Una propuesta de licencia clara, premium e inmediatamente negociable.",
    contractBody:
      "La estructura financiera combina activación, exclusividad territorial y royalties para simplificar la decisión del retail preservando el margen de alto valor de TryOnYou.",
    contractLabels: [
      "Setup fee",
      "Exclusividad territorial",
      "Royalties sobre ventas",
      "Total inmediato",
    ],
    pricingTag: "OFERTA COMERCIAL",
    pricingTitle: "Tres puertas de entrada, una misma firma de lujo digital.",
    pricingLead:
      "Desde la validación en tienda hasta el despliegue multi-site, el pricing mantiene la deseabilidad del producto y facilita la adopción B2B.",
    pricingCards: [
      {
        title: "Pilote Gratuit",
        price: "1 mes gratis",
        badge: "Descubrimiento",
        description: "Un mes para demostrar la subida de conversión, afinar el ritual de prueba y formar a los equipos de tienda.",
        features: [
          "1 espejo Divineo en test",
          "Soporte de onboarding maison",
          "Métricas de conversión y devolución",
        ],
        cta: "Activar piloto",
        action: "pilot",
      },
      {
        title: "Divineo Pro",
        price: "299€/mo",
        badge: "Recomendado",
        description: "El formato ideal para un corner premium que quiere vender más sin saturar el espacio ni la experiencia.",
        features: [
          "Asistente P.A.U. orquestado",
          "Checkout soberano en EUR",
          "Soporte comercial prioritario",
        ],
        cta: "Hablar con ventas",
        action: "pro",
        highlight: true,
      },
      {
        title: "Divineo Enterprise",
        price: "A medida",
        badge: "Maison & grupo",
        description: "Para redes de lujo, grandes almacenes y despliegues internacionales con gobernanza a medida.",
        features: [
          "Despliegue multi-site",
          "Integración CRM / data room",
          "Condiciones exclusivas para inversores",
        ],
        cta: "Abrir mandato",
        action: "enterprise",
      },
    ],
    pauTag: "ASISTENTE MAISON",
    pauTitle: "P.A.U., la presencia digital que guía, tranquiliza y cierra la venta.",
    pauLead:
      "Pensado como un concierge couture impulsado por IA, P.A.U. traduce la biometría en deseo y lleva la prueba al momento decisivo: The Snap.",
    pauBody:
      "La guía acompaña a la clienta, estructura el ritual y transforma la duda en certeza soberana sin romper jamás la estética de la maison.",
    pauCapabilityTitle: "Ritual guiado",
    pauCapabilities: [
      "Bienvenida y preparación emocional",
      "Escaneo de silueta con precisión biométrica",
      "Revelación instantánea de un nuevo look",
    ],
    pauLiveLabel: "Estado live",
    pauSnapCta: "Disparar The Snap",
    pauStatusReady: "P.A.U. está autorizado y listo para operar.",
    pauStatusLocked: "P.A.U. espera un nodo autorizado o un UserCheck activo.",
    footerLine: "Contacto maison: info@tryonyou.app · París · Galeries Lafayette · Investor-ready experience",
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

  const heroSectionRef = useRef<HTMLElement | null>(null);
  const heroReveal = useScrollReveal<HTMLElement>();
  const manifestoReveal = useScrollReveal<HTMLElement>();
  const technologyReveal = useScrollReveal<HTMLElement>();
  const collectionReveal = useScrollReveal<HTMLElement>();
  const patentReveal = useScrollReveal<HTMLElement>();
  const pricingReveal = useScrollReveal<HTMLElement>();
  const pauReveal = useScrollReveal<HTMLElement>();

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
      setNavScrolled(window.scrollY > heroHeight * 0.55);
    };

    updateNavbarState();
    window.addEventListener("scroll", updateNavbarState, { passive: true });
    window.addEventListener("resize", updateNavbarState);

    return () => {
      window.removeEventListener("scroll", updateNavbarState);
      window.removeEventListener("resize", updateNavbarState);
    };
  }, []);

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
                <em>Maison Digitale</em>
              </span>
            </a>

            <nav className="site-nav__links" aria-label="Primary">
              {pageCopy.navLinks.map((item) => (
                <a key={item.href} href={item.href} onClick={(event) => handleAnchorClick(event, item.href)}>
                  {item.label}
                </a>
              ))}
            </nav>

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
        </header>

        <main className="landing-main">
          <section
            id="hero"
            ref={bindHeroSection}
            className="landing-section hero-section"
            data-visible={heroReveal.visible ? "1" : undefined}
          >
            <div className="hero-layout">
              <div className="hero-copy-col">
                <div className="hero-brand-row">
                  <div className="hero-brand-lockup">
                    {BRANDS_MAESTROS.map((brand) => (
                      <span key={brand}>{brand}</span>
                    ))}
                  </div>
                  <span className="hero-meta-chip">{pageCopy.heroMeta}</span>
                </div>

                <p className="section-tag">{copy.badge}</p>
                <h1 className="hero-title">{copy.heroTitle}</h1>
                <p className="hero-lead">{copy.heroLead}</p>

                <div className="hero-capture-row">
                  <input
                    type="email"
                    value={emailHero}
                    onChange={(e: ChangeEvent<HTMLInputElement>) =>
                      setEmailHero(e.target.value)
                    }
                    placeholder={copy.heroEmailPlaceholder}
                    className="hero-email-input"
                  />
                  <button
                    type="button"
                    onClick={() => void onHeroSubmit()}
                    className="btn-primary"
                  >
                    {copy.heroCta}
                  </button>
                </div>

                <div className="hero-action-row">
                  <button
                    type="button"
                    className="btn-secondary"
                    onMouseEnter={() => setPauInaugurationWhisper(pauInaugurationCompliment())}
                    onFocus={() => setPauInaugurationWhisper(pauInaugurationCompliment())}
                    onClick={onInaugurationStripeCharge}
                    aria-label={copy.inaugurationAriaLabel}
                    title={pauInaugurationWhisper || copy.inaugurationTitle}
                  >
                    {copy.inaugurationCta}
                  </button>
                  <button
                    type="button"
                    className="btn-tertiary"
                    onClick={() => void postBetaWaitlist(copy)}
                  >
                    {pageCopy.heroSecondaryCta}
                  </button>
                </div>

                {pauInaugurationWhisper ? (
                  <p className="hero-whisper">PAU · {pauInaugurationWhisper}</p>
                ) : null}

                <div className="hero-house-phrases">
                  {copy.housePhrases.map((phrase) => (
                    <p key={phrase}>« {phrase} »</p>
                  ))}
                </div>

                <div className="hero-link-row">
                  <a
                    href={getDivineoCheckoutUrl()}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hero-inline-link"
                  >
                    {SOVEREIGN_FIT_LABEL}
                  </a>
                  <span>{copy.checkoutHint}</span>
                </div>
              </div>

              <motion.div
                className="hero-feature-card"
                initial={{ opacity: 0, y: 26 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              >
                <span className="hero-feature-card__label">{pageCopy.heroPanelLabel}</span>
                <h2>{pageCopy.heroPanelTitle}</h2>
                <p>{pageCopy.heroPanelBody}</p>

                <div className="hero-status-grid">
                  <article>
                    <span>{pageCopy.heroContractKicker}</span>
                    <strong>{pauDistrictLabel}</strong>
                    <p>{pageCopy.heroContractBody}</p>
                  </article>
                  <article>
                    <span>Jules lane</span>
                    <strong>{julesLane}</strong>
                    <p>{copy.manifestoLafayette}</p>
                  </article>
                  <article>
                    <span>Elastic signal</span>
                    <strong>{elasticLabel}</strong>
                    <p>{pauStarted ? pageCopy.pauStatusReady : pageCopy.pauStatusLocked}</p>
                  </article>
                </div>

                <div className="hero-media-grid">
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
              </motion.div>
            </div>
          </section>

          <section
            id="manifesto"
            ref={manifestoReveal.ref}
            className="landing-section manifesto-section"
            data-visible={manifestoReveal.visible ? "1" : undefined}
          >
            <div className="section-heading section-heading--centered">
              <p className="section-tag">{copy.manifestoTag}</p>
              <h2>{copy.manifestoTitle}</h2>
              <p>{pageCopy.manifestoIntro}</p>
            </div>

            <div className="manifesto-grid">
              <article
                className="manifesto-panel manifesto-panel--lead"
                style={{ ["--manifesto-delay" as const]: "0.08s" }}
              >
                <span className="manifesto-panel__label">{pageCopy.manifestoQuoteLabel}</span>
                <blockquote>{copy.manifestoBody}</blockquote>
              </article>
              <article
                className="manifesto-panel"
                style={{ ["--manifesto-delay" as const]: "0.16s" }}
              >
                <p>{copy.manifestoAccumulation}</p>
              </article>
              <article
                className="manifesto-panel"
                style={{ ["--manifesto-delay" as const]: "0.24s" }}
              >
                <p>{copy.manifestoColor}</p>
              </article>
              <article
                className="manifesto-panel manifesto-panel--accent"
                style={{ ["--manifesto-delay" as const]: "0.32s" }}
              >
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
                  <strong>THE 0SIZES ERA</strong>
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
            id="collection"
            ref={collectionReveal.ref}
            className="landing-section collection-section"
            data-visible={collectionReveal.visible ? "1" : undefined}
          >
            <div className="section-heading section-heading--centered">
              <p className="section-tag">{pageCopy.collectionTag}</p>
              <h2>{pageCopy.collectionTitle}</h2>
              <p>{pageCopy.collectionLead}</p>
            </div>

            <div className="collection-grid">
              {lafayetteCollection.map((garment) => (
                <article key={garment.id} className="collection-card">
                  <div className="collection-card__media">
                    <img src={garment.image} alt={`${garment.brand} ${garment.name}`} loading="lazy" />
                    <span className="collection-card__tag">{garment.tag}</span>
                  </div>
                  <div className="collection-card__body">
                    <div className="collection-card__topline">
                      <span>{garment.brand}</span>
                      <strong>{formatEurAmount(garment.price, locale)}</strong>
                    </div>
                    <h3>{garment.name}</h3>
                    <p>{garment.category}</p>
                    <div className="collection-card__meta">
                      <span>{pageCopy.collectionFabricLabel}</span>
                      <strong>{garment.fabric}</strong>
                    </div>
                    <div className="collection-card__meta">
                      <span>{pageCopy.collectionPrecisionLabel}</span>
                      <strong>{garment.precision.toFixed(1)}%</strong>
                    </div>
                    <div className="collection-card__swatch-row">
                      <span className="collection-card__swatch" style={{ backgroundColor: garment.color }} />
                      <span>{garment.color_name}</span>
                    </div>
                    <div className="collection-card__profiles">
                      <span>{pageCopy.collectionProfilesLabel}</span>
                      <ul>
                        {garment.fit_profile.map((profile) => (
                          <li key={profile}>{profile}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section
            id="patent-contract"
            ref={patentReveal.ref}
            className="landing-section patent-section"
            data-visible={patentReveal.visible ? "1" : undefined}
          >
            <div className="patent-layout">
              <article className="patent-card">
                <p className="section-tag">{pageCopy.patentTag}</p>
                <h2>{pageCopy.patentTitle}</h2>
                <p>{pageCopy.patentBody}</p>
                <div className="patent-card__chips">
                  <span>PCT/EP2025/067317</span>
                  <span>8 Super-Claims</span>
                  <span>17M€ — 26M€</span>
                </div>
              </article>

              <article className="contract-card">
                <p className="section-tag">{pageCopy.contractTag}</p>
                <h2>{pageCopy.contractTitle}</h2>
                <p>{pageCopy.contractBody}</p>

                <div className="contract-grid">
                  {[
                    { label: pageCopy.contractLabels[0], value: formatEurAmount(12500, locale) },
                    { label: pageCopy.contractLabels[1], value: formatEurAmount(15000, locale) },
                    { label: pageCopy.contractLabels[2], value: "8%" },
                    { label: pageCopy.contractLabels[3], value: formatEurAmount(27500, locale) },
                  ].map((item) => (
                    <div key={item.label} className="contract-metric">
                      <span>{item.label}</span>
                      <strong>{item.value}</strong>
                    </div>
                  ))}
                </div>

                <button type="button" className="btn-secondary btn-secondary--full" onClick={onLafayetteStripeCharge}>
                  {copy.lafayetteCta}
                </button>
              </article>
            </div>
          </section>

          <section
            id="pricing"
            ref={pricingReveal.ref}
            className="landing-section pricing-section"
            data-visible={pricingReveal.visible ? "1" : undefined}
          >
            <div className="section-heading section-heading--centered">
              <p className="section-tag">{pageCopy.pricingTag}</p>
              <h2>{pageCopy.pricingTitle}</h2>
              <p>{pageCopy.pricingLead}</p>
            </div>

            <div className="pricing-grid">
              {pageCopy.pricingCards.map((card) => (
                <article
                  key={card.title}
                  className={`pricing-card${card.highlight ? " pricing-card--highlight" : ""}`}
                >
                  <span className="pricing-card__badge">{card.badge}</span>
                  <h3>{card.title}</h3>
                  <p className="pricing-card__price">{card.price}</p>
                  <p className="pricing-card__description">{card.description}</p>
                  <ul className="pricing-card__features">
                    {card.features.map((feature) => (
                      <li key={feature}>{feature}</li>
                    ))}
                  </ul>
                  <button
                    type="button"
                    className={card.highlight ? "btn-primary btn-primary--full" : "btn-secondary btn-secondary--full"}
                    onClick={() => handlePricingAction(card.action)}
                  >
                    {card.cta}
                  </button>
                </article>
              ))}
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
                  <p>{julesLane}</p>
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
                  <button type="button" className="btn-tertiary" onClick={() => void postBetaWaitlist(copy)}>
                    {copy.betaCta}
                  </button>
                </div>
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

        <footer className="app-footer">
          <div className="app-footer__top">
            <div>
              <strong>TRYONYOU</strong>
              <p>{pageCopy.footerLine}</p>
              <p className="app-footer__tagline">PA, PA, PA. LET'S BE THE TENDENCY.</p>
            </div>
            <div className="app-footer__links">
              <a href="mailto:info@tryonyou.app">info@tryonyou.app</a>
              <a href="https://www.linkedin.com" target="_blank" rel="noopener noreferrer">
                LinkedIn
              </a>
              <a href="https://www.instagram.com" target="_blank" rel="noopener noreferrer">
                Instagram
              </a>
            </div>
          </div>
          <div className="app-legal">
            SIRET 94361019600017 · PCT/EP2025/067317 · TRYONYOU V11 SOVEREIGN
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
