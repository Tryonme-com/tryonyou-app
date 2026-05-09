/**
 * Maison Couture Nocturne — Home composition.
 *
 * Section order (editorial chapters with roman numerals):
 *   I.  Le problème
 *   II. Démo Live (try-on interactive)
 *   III. La solution + miroir intelligent
 *   IV. Technologie & brevet
 *   V.  Pilote Maison
 *   VI. Contact
 */
import { useReveal } from "@/hooks/useReveal";
import SiteHeader from "@/components/sections/SiteHeader";
import Hero from "@/components/sections/Hero";
import Problem from "@/components/sections/Problem";
import DemoSection from "@/components/sections/DemoSection";
import Solution from "@/components/sections/Solution";
import Technology from "@/components/sections/Technology";
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
        <VideoFeature />
        <BoutiqueVideo />
        <Technology />
        <PilotOffer />
        <Contact />
      </main>
      <SiteFooter />
    </div>
  );
}
