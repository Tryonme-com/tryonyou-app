/**
 * Landing LVT — hero «Versace Master Look» + espejo Pau (motor 3D / smokey).
 * Activa con ?lvt=1 en la URL.
 *
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 * Bajo Protocolo de Soberanía V10 - Founder: Rubén
 */
import { ORO_DIVINEO, SOVEREIGN_FIT_LABEL } from "../divineo/divineoV11Config";
import RealTimeAvatar from "./RealTimeAvatar";
import "./LandingLVT.css";

type Props = {
  pauStarted: boolean;
};

export default function LandingLVT({ pauStarted }: Props) {
  const oro = ORO_DIVINEO;

  return (
    <div className="landing-lvt-root landing-container">
      <section className="landing-lvt-hero">
        <p className="landing-lvt-kicker">
          {SOVEREIGN_FIT_LABEL} · Live It
        </p>
        <h1 className="landing-lvt-title">VERSACE MASTER LOOK</h1>

        <div id="pau-mirror-container" className="landing-lvt-mirror pau-mirror">
          <div className="golden-swirl-particles" aria-hidden />
          <div className="landing-lvt-mirror-stage">
            <RealTimeAvatar
              variant="lafayette"
              disabled={!pauStarted}
              videoId="lvt-versace-master"
            />
          </div>
        </div>

        <p className="landing-lvt-lede">
          La precisión de la Talla Perfecta se une al Divineo de Versace. Un chasquido, tu look
          completo.
        </p>

        <a
          href="./"
          className="landing-lvt-back"
          style={{ borderBottomColor: oro, color: oro }}
        >
          Volver al espejo principal
        </a>
      </section>
    </div>
  );
}
