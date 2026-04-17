/**
 * Agent #10 — Runway Generator
 * Genera configuraciones de pasarela virtual para presentaciones de marca.
 */

const RUNWAY_THEMES = {
  LAFAYETTE: { background: "#1a1410", accent: "#d4af37", font: "Cinzel" },
  MARAIS: { background: "#0d0d0d", accent: "#c8102e", font: "Playfair Display" },
  CHAMPS: { background: "#f5f0e8", accent: "#26201A", font: "Cormorant Garamond" },
};

export function generateRunwayConfig({ theme = "LAFAYETTE", brands, garments }) {
  const t = RUNWAY_THEMES[theme] || RUNWAY_THEMES.LAFAYETTE;
  return {
    theme: t,
    brands: brands || [],
    garments: garments || [],
    sequence: (garments || []).map((g, i) => ({
      order: i + 1,
      garment: g.name,
      brand: g.brand,
      duration: 8,
      transition: "fade-gold",
    })),
    totalDuration: (garments || []).length * 8,
    music: "orchestral-luxury",
  };
}

export default { generateRunwayConfig, RUNWAY_THEMES };
