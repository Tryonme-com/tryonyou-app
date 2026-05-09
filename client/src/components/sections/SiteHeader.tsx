/**
 * Maison Couture Nocturne — sticky header.
 * Style file reminders:
 * - Asymmetric: logo left, nav center, CTA right
 * - Hairline gold separator on scroll
 * - All-caps Inter 11px / 0.18em tracking
 */
import { useEffect, useState } from "react";

const NAV = [
  { id: "probleme", label: "Le problème" },
  { id: "solution", label: "La solution" },
  { id: "demo", label: "Démo" },
  { id: "technologie", label: "Technologie" },
  { id: "pilote", label: "Pilote" },
  { id: "contact", label: "Contact" },
];

export default function SiteHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 30);
    handler();
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  const handleAnchor = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    setOpen(false);
  };

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-700 ${
        scrolled
          ? "backdrop-blur-md bg-[rgba(10,8,7,0.82)] border-b border-[rgba(201,168,76,0.25)]"
          : "bg-transparent"
      }`}
    >
      <div className="container flex items-center justify-between h-[72px] md:h-[88px]">
        <a href="#hero" onClick={handleAnchor("hero")} className="group flex items-center gap-3">
          <span
            className="text-[var(--color-or)] font-display italic tracking-tight text-[22px] md:text-[26px]"
            style={{ fontFamily: "var(--font-display)" }}
          >
            TRYONYOU
          </span>
          <span className="hidden md:inline-block w-[1px] h-4 bg-[rgba(201,168,76,0.5)]" />
          <span className="hidden md:inline-block text-[10px] tracking-[0.32em] uppercase text-[var(--color-fog)]">
            Maison Tech&nbsp;·&nbsp;Paris
          </span>
        </a>

        <nav className="hidden lg:flex items-center gap-8">
          {NAV.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              onClick={handleAnchor(item.id)}
              className="text-[12px] tracking-[0.18em] uppercase text-[var(--color-ivoire)]/80 hover:text-[var(--color-or)] transition-colors duration-500"
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="hidden lg:flex">
          <a href="#contact" onClick={handleAnchor("contact")} className="btn-or">
            Demander une démo
          </a>
        </div>

        <button
          aria-label="Menu"
          className="lg:hidden text-[var(--color-or)]"
          onClick={() => setOpen((s) => !s)}
        >
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <path
              d={open ? "M6 6 L22 22 M22 6 L6 22" : "M4 8 L24 8 M4 14 L24 14 M4 20 L24 20"}
              stroke="currentColor"
              strokeWidth="1.4"
              strokeLinecap="square"
            />
          </svg>
        </button>
      </div>

      {/* Mobile sheet */}
      <div
        className={`lg:hidden overflow-hidden transition-[max-height] duration-700 ${
          open ? "max-h-[80vh]" : "max-h-0"
        }`}
      >
        <div className="container py-6 border-t border-[rgba(201,168,76,0.2)] bg-[var(--color-noir)]/95 backdrop-blur-md">
          <ul className="flex flex-col gap-4">
            {NAV.map((item) => (
              <li key={item.id}>
                <a
                  href={`#${item.id}`}
                  onClick={handleAnchor(item.id)}
                  className="block text-[14px] tracking-[0.18em] uppercase text-[var(--color-ivoire)]/85 hover:text-[var(--color-or)] py-2"
                >
                  {item.label}
                </a>
              </li>
            ))}
            <li className="pt-3">
              <a href="#contact" onClick={handleAnchor("contact")} className="btn-or w-full justify-center">
                Demander une démo
              </a>
            </li>
          </ul>
        </div>
      </div>
    </header>
  );
}
