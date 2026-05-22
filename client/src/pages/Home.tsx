/**
 * Maison Couture Nocturne — Home composition.
 *
 * Section order (editorial chapters with roman numerals):
 *   I.   Hero / Problème
 *   II.  Démo Live (try-on interactive)
 *   III. La solution + miroir intelligent
 *   IV.  Le Protocole Zero-Size (Gemelas)
 *   V.   Vidéo / Boutique
 *   VI.  Technologie & brevet
 *   VII. Architecture ABVETOS
 *   VIII.Forteresse IP
 *   IX.  Roadmap 2026—2028
 *   X.   Pilote Maison
 *   XI.  Contact
 */
import { useReveal } from "@/hooks/useReveal";
import SiteHeader from "@/components/sections/SiteHeader";
import Hero from "@/components/sections/Hero";
import Problem from "@/components/sections/Problem";
import DemoSection from "@/components/sections/DemoSection";
import Solution from "@/components/sections/Solution";
import ZeroSizeProtocol from "@/components/sections/ZeroSizeProtocol";
import Technology from "@/components/sections/Technology";
import AbvetosArchitecture from "@/components/sections/AbvetosArchitecture";
import ForteresseIP from "@/components/sections/ForteresseIP";
import Roadmap from "@/components/sections/Roadmap";
import VideoFeature from "@/components/sections/VideoFeature";
import BoutiqueVideo from "@/components/sections/BoutiqueVideo";
import PilotOffer from "@/components/sections/PilotOffer";
import Contact from "@/components/sections/Contact";
import SiteFooter from "@/components/sections/SiteFooter";
import { useSeoMetadata } from "@/hooks/useSeoMetadata";

export default function Home() {
  useReveal();
  useSeoMetadata({
    title: "Cómo Reducir un 30% las Devoluciones en Retail | TryOnYou",
    description:
      "Solución técnica para tiendas de moda. Amortización garantizada al segundo mes. Integra nuestra API sin almacenar datos biométricos según RGPD.",
    keywords: [
      "optimización de inventario retail",
      "reducir devoluciones moda e-commerce",
      "tecnología para probadores físicos",
      "ROI retail vision",
      "logística inversa textil",
    ],
    openGraph: {
      title: "Cómo Reducir un 30% las Devoluciones en Retail | TryOnYou",
      description:
        "Solución técnica para tiendas de moda. Amortización garantizada al segundo mes. Integra nuestra API sin almacenar datos biométricos según RGPD.",
      type: "article",
      image: "/images/gemelo-digital.jpg",
    },
    structuredData: {
      "@context": "https://schema.org",
      "@type": "TechArticle",
      headline: "Amortización inmediata en tecnología de probadores digitales",
      description:
        "Solución técnica para tiendas de moda. Amortización garantizada al segundo mes. Integra nuestra API sin almacenar datos biométricos según RGPD.",
      profitabilityMetric: "2nd month ROI",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Cloud / API-First",
      articleBody:
        "El empresario de retail actual exige respuestas directas: ganar más o gastar menos. TryOnYou ofrece una amortización de sus cobros al segundo mes de implantación. Nuestra tecnología para probadores físicos y digitales resuelve el principal dolor financiero del sector textil: el coste operativo de las devoluciones de ropa, garantizando el tallaje correcto mediante computación en el Edge sin registrar datos sensibles.",
      keywords: [
        "optimización de inventario retail",
        "reducir devoluciones moda e-commerce",
        "tecnología para probadores físicos",
        "ROI retail vision",
        "logística inversa textil",
      ],
      inLanguage: "es",
    },
  });

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-noir)]">
      <SiteHeader />
      <main className="flex-1">
        <Hero />
        <Problem />
        <DemoSection />
        <Solution />
        <ZeroSizeProtocol />
        <VideoFeature />
        <BoutiqueVideo />
        <Technology />
        <AbvetosArchitecture />
        <ForteresseIP />
        <Roadmap />
        <PilotOffer />
        <Contact />
      </main>
      <SiteFooter />
    </div>
  );
}
