export interface GarmentOverlayConfig {
  id: string;
  name: string;
  imagePath: string;
  scaleFactor: number;
  offsetY: number;
}

export const LAFAYETTE_OVERLAYS: Record<string, GarmentOverlayConfig> = {
  // --- ASSETS BALMAIN ---
  "blm_01": { id: "blm_01", name: "Blazer Cruzado Estructurado Pierre", imagePath: "/assets/balmain_blazer.png", scaleFactor: 1.15, offsetY: -5 },
  "blm_02": { id: "blm_02", name: "Vestido Knit Monograma Geométrico", imagePath: "/assets/balmain_dress.png", scaleFactor: 1.10, offsetY: 10 },
  "blm_03": { id: "blm_03", name: "Chaqueta Tweed Botones de Oro Vintage", imagePath: "/assets/balmain_tweed.png", scaleFactor: 1.12, offsetY: -2 },
  "blm_04": { id: "blm_04", name: "Top Corsé de Neopreno Satinado", imagePath: "/assets/balmain_corset.png", scaleFactor: 1.05, offsetY: 5 },
  "blm_05": { id: "blm_05", name: "Abrigo Largo Masculino de Lana Negra", imagePath: "/assets/balmain_coat.png", scaleFactor: 1.18, offsetY: -8 },

  // --- ASSETS PRADA ---
  "prd_01": { id: "prd_01", name: "Abrigo Re-Nylon Minimalista Anthracite", imagePath: "/assets/prada_coat.png", scaleFactor: 1.20, offsetY: 0 },
  "prd_02": { id: "prd_02", name: "Falda Plisada de Sarga Estructurada", imagePath: "/assets/prada_skirt.png", scaleFactor: 1.05, offsetY: 45 },
  "prd_03": { id: "prd_03", name: "Traje Técnico Gabardina de Corte Sastre", imagePath: "/assets/prada_suit.png", scaleFactor: 1.18, offsetY: -4 },
  "prd_04": { id: "prd_04", name: "Chaqueta Corta de Cuero Gastado Umber", imagePath: "/assets/prada_leather.png", scaleFactor: 1.14, offsetY: 2 },
  "prd_05": { id: "prd_05", name: "Vestido Popelín con Escote Geométrico", imagePath: "/assets/prada_dress.png", scaleFactor: 1.08, offsetY: 12 },

  // --- ASSETS HERMÈS ---
  "rms_01": { id: "rms_01", name: "Capa Corta en Cachemira Bone Hermès", imagePath: "/assets/hermes_cape.png", scaleFactor: 1.25, offsetY: -15 },
  "rms_02": { id: "rms_02", name: "Pañuelo de Seda Estampado Art Deco", imagePath: "/assets/hermes_scarf.png", scaleFactor: 0.90, offsetY: -30 },
  "rms_03": { id: "rms_03", name: "Chaqueta de Piel Flexible Suave Ecuestre", imagePath: "/assets/hermes_leather.png", scaleFactor: 1.16, offsetY: -6 },
  "rms_04": { id: "rms_04", name: "Jersey Cuello Alto Hilo Trenzado Lino", imagePath: "/assets/hermes_knit.png", scaleFactor: 1.10, offsetY: -1 },
  "rms_05": { id: "rms_05", name: "Pantalón Recto de Lana de Sastrería", imagePath: "/assets/hermes_pants.png", scaleFactor: 1.02, offsetY: 38 }
};

export function getAdjustedOverlay(garmentId: string, userHeightPx: number): GarmentOverlayConfig | null {
  const config = LAFAYETTE_OVERLAYS[garmentId];
  if (!config) return null;
  return {
    ...config,
    scaleFactor: config.scaleFactor * (userHeightPx / 800)
  };
}
