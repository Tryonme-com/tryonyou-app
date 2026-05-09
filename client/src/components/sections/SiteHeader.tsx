/**
 * Maison Couture Nocturne — sticky header.
 *
 * Smart navigation:
 *   - On the home page (/) anchor links scroll to sections.
 *   - On other pages, anchor links navigate back to /#section.
 *   - Route links (Try-On, Catalogue, Foot Scan, Investors) go through wouter.
 */
import { useEffect, useState } from "react";
import { Link, useLocation } from "wouter";

const ANCHORS = [
  { id: "probleme", label: "Le problème" },
  { id: "solution", label: "La solution" },
  { id: "technologie", label: "Technologie" },
  { id: "pilote", label: "Pilote" },
];

const ROUTES = [
  { href: "/tryon", label: "Try-On" },
  { href: "/catalogue", label: "Catalogue" },
  { href: "/footscan", label: "Foot Scan" },
  { href: "/investors", label: "Investors" },
];

export default function SiteHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [location, setLocation] = useLocation();
  const isHome = location === "/" || location === "";

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 30);
    handler();
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  const goAnchor = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    setOpen(false);
    if (isHome) {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      // Navigate home then scroll
      setLocation("/");
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 80);
    }
  };

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-700 ${
        scrolled || !isHome
          ? "backdrop-blur-md bg-[rgba(10,8,7,0.82)] border-b border-[rgba(201,168,76,0.25)]"
          : "bg-transparent"
      }`}
    >
      <div className="container flex items-center justify-between h-[72px] md:h-[88px]">
        <Link
          href="/"
          className="group flex items-center gap-3"
          onClick={() => setOpen(false)}
        >
          <span
            className="text-[var(--color-or)] font-display italic tracking-tight text-[22px] md:text-[26px]"
            style={{ fontFamily: "var(--font-display)" }}
          >
            TRYONYOU
          </span>
          <span className="hidden xl:inline-block w-[1px] h-4 bg-[rgba(201,168,76,0.5)]" />
          <span className="hidden xl:inline-block text-[10px] tracking-[0.32em] uppercase text-[var(--color-fog)]">
            Maison Tech&nbsp;·&nbsp;Paris
          </span>
        </Link>

        <nav className="hidden lg:flex items-center gap-5 xl:gap-7">
          {ROUTES.map((r) => (
            <Link
              key={r.href}
              href={r.href}
              className={`text-[11px] xl:text-[12px] tracking-[0.18em] uppercase whitespace-nowrap transition-colors duration-500 ${
                location.startsWith(r.href)
                  ? "text-[var(--color-or)]"
                  : "text-[var(--color-ivoire)]/80 hover:text-[var(--color-or)]"
              }`}
            >
              {r.label}
            </Link>
          ))}
          <span className="hidden xl:inline-block w-[1px] h-3 bg-white/15" />
          {ANCHORS.map((a) => (
            <a
              key={a.id}
              href={`#${a.id}`}
              onClick={goAnchor(a.id)}
              className="hidden xl:inline-block text-[12px] tracking-[0.18em] uppercase whitespace-nowrap text-[var(--color-ivoire)]/65 hover:text-[var(--color-or)] transition-colors duration-500"
            >
              {a.label}
            </a>
          ))}
        </nav>

        <div className="hidden lg:flex">
          <Link href="/tryon" className="btn-or whitespace-nowrap">
            Lancer la démo
          </Link>
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
          open ? "max-h-[90vh]" : "max-h-0"
        }`}
      >
        <div className="container py-6 border-t border-[rgba(201,168,76,0.2)] bg-[var(--color-noir)]/95 backdrop-blur-md">
          <ul className="flex flex-col gap-3">
            {ROUTES.map((r) => (
              <li key={r.href}>
                <Link
                  href={r.href}
                  className="block text-[14px] tracking-[0.18em] uppercase text-[var(--color-or)] py-2"
                  onClick={() => setOpen(false)}
                >
                  {r.label}
                </Link>
              </li>
            ))}
            <li className="my-2 hairline" />
            {ANCHORS.map((a) => (
              <li key={a.id}>
                <a
                  href={`#${a.id}`}
                  onClick={goAnchor(a.id)}
                  className="block text-[14px] tracking-[0.18em] uppercase text-[var(--color-ivoire)]/80 py-2"
                >
                  {a.label}
                </a>
              </li>
            ))}
            <li className="pt-3">
              <Link
                href="/tryon"
                className="btn-or w-full justify-center"
                onClick={() => setOpen(false)}
              >
                Lancer la démo
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </header>
  );
}
