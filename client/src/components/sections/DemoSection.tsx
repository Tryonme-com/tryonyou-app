/**
 * Maison Couture Nocturne — Demo section.
 * Composes: WebcamAvatar (live MediaPipe → Three.js), DigitalMirrorPanel,
 * FabricSimulator. Three layers of the TRYONYOU experience for executives.
 */
import WebcamAvatar from "@/components/demo/WebcamAvatar";
import DigitalMirrorPanel from "@/components/demo/DigitalMirrorPanel";
import FabricSimulator from "@/components/demo/FabricSimulator";

export default function DemoSection() {
  return (
    <section id="demo" className="relative py-24 md:py-36 bg-[var(--color-noir)]">
      <div className="container">
        <div className="hairline mb-16 reveal-up" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-16">
          <div className="lg:col-span-5 reveal-up">
            <div className="roman mb-6">II</div>
            <span className="eyebrow mb-5 inline-flex">Démo Live</span>
            <h2 className="display-l">
              Essayez,
              <br />
              <span className="accent-italic">en direct.</span>
            </h2>
          </div>
          <div className="lg:col-span-6 lg:col-start-7 lg:pt-6 reveal-up" data-delay="160">
            <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/85 mb-4">
              Trois couches de l'expérience TRYONYOU sont opérationnelles dans votre
              navigateur&nbsp;: l'<span className="accent-italic">avatar temps réel</span> (MediaPipe → Kalidokit → Three.js),
              le <span className="accent-italic">miroir digital boutique</span>, et la
              <span className="accent-italic"> simulation textile</span> (drapé physique
              CAP). Aucune donnée ne quitte votre machine.
            </p>
          </div>
        </div>

        <div className="reveal-up mb-16">
          <WebcamAvatar />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 reveal-up" data-delay="200">
          <DigitalMirrorPanel />
          <FabricSimulator />
        </div>
      </div>
    </section>
  );
}
