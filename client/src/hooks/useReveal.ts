import { useEffect } from "react";

/**
 * Adds an IntersectionObserver that toggles `is-visible` on .reveal-up elements.
 * Maison Couture Nocturne — animations: 900ms cubic-bezier(0.16, 1, 0.3, 1), staggered.
 */
export function useReveal() {
  useEffect(() => {
    if (typeof window === "undefined" || !("IntersectionObserver" in window)) return;
    const elements = Array.from(document.querySelectorAll<HTMLElement>(".reveal-up"));
    if (!elements.length) return;

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const el = entry.target as HTMLElement;
            const idx = Number(el.dataset.delay ?? 0);
            window.setTimeout(() => el.classList.add("is-visible"), idx);
            io.unobserve(el);
          }
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" },
    );
    elements.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
}
