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

export default function Home() {
  useReveal();

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
