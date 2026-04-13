import { useEffect } from "react";
import { initTryOnYouAnimation } from "../lib/tryOnYouAnimation";

const LOOKS = [
  { id: 1, label: "Look Maestro I" },
  { id: 2, label: "Look Maestro II" },
  { id: 3, label: "Look Maestro III" },
  { id: 4, label: "Look Maestro IV" },
  { id: 5, label: "Look Maestro V" },
];

export function MacbookSection() {
  useEffect(() => {
    initTryOnYouAnimation();
  }, []);

  return (
    <section className="macbook-section">
      <div className="macbook-wrap">
        <div className="macbook-base" />
        <div className="macbook-lid">
          <div className="macbook-screen">
            <img
              src="/assets/logo_tryonyou_official.png"
              alt="TryOnYou"
              className="macbook-screen__logo"
            />
            <div className="macbook-looks-grid">
              {LOOKS.map((look) => (
                <div key={look.id} className="look-card">
                  <span>{look.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
