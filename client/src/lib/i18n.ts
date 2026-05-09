/**
 * TRYONYOU — Multi-langue (FR, EN, ES) pour la page /tryon.
 */

export type Lang = "fr" | "en" | "es";

export const LANG_PACKS: Record<Lang, {
  brand: string;
  patent: string;
  permissionTitle: string;
  permissionLede: string;
  permissionCTA: string;
  permissionDenied: string;
  scanning: string;
  measuring: string;
  bodyDetected: string;
  fitOptimal: string;
  fitRecalc: string;
  reserveCabin: string;
  showMore: string;
  curated: string;
  fabric: string;
  drape: string;
  back: string;
  designer: string;
  perfectFit: string;
  recalculating: string;
  validatedBy: string;
  collection: string;
  phaseCalibration: string;
  phaseAnalysis: string;
  phaseMaterializing: string;
  phaseReady: string;
  faceCamera: string;
}> = {
  fr: {
    brand: "TRYONYOU",
    patent: "Brevet PCT/EP2025/067317",
    permissionTitle: "Activer la caméra",
    permissionLede: "Pour projeter le vêtement sur votre silhouette en temps réel, TRYONYOU a besoin d'accéder à votre caméra. Aucune image n'est enregistrée.",
    permissionCTA: "Activer la caméra",
    permissionDenied: "Accès caméra refusé. Réessayez en autorisant l'accès dans les réglages du navigateur.",
    scanning: "Scan biométrique en cours…",
    measuring: "Détection du corps en cours…",
    bodyDetected: "Corps détecté. Comparaison avec la base de données…",
    fitOptimal: "Ajustement optimal — Projection autorisée",
    fitRecalc: "Robert recalcule pour optimiser le drapé…",
    reserveCabin: "Réserver en Cabine",
    showMore: "Voir plus",
    curated: "Sélection curatée pour vous",
    fabric: "Tissu",
    drape: "Tombé",
    back: "Retour",
    designer: "Designer",
    perfectFit: "AJUSTEMENT : PARFAIT",
    recalculating: "Robert recalcule…",
    validatedBy: "Validé par le moteur Jules — Divineo Glow",
    collection: "Collection Lafayette",
    phaseCalibration: "Calibration",
    phaseAnalysis: "Analyse de silhouette",
    phaseMaterializing: "Matérialisation de la pièce",
    phaseReady: "Projection prête",
    faceCamera: "Placez-vous face à la caméra, à 1,5 m",
  },
  en: {
    brand: "TRYONYOU",
    patent: "Patent PCT/EP2025/067317",
    permissionTitle: "Enable camera",
    permissionLede: "To project the garment on your silhouette in real time, TRYONYOU needs camera access. No images are stored.",
    permissionCTA: "Enable camera",
    permissionDenied: "Camera access denied. Please allow access in your browser settings.",
    scanning: "Biometric scan in progress…",
    measuring: "Body detection in progress…",
    bodyDetected: "Body detected. Comparing against database…",
    fitOptimal: "Optimal fit — Projection authorized",
    fitRecalc: "Robert is recalculating drape…",
    reserveCabin: "Reserve a Fitting Room",
    showMore: "Show more",
    curated: "Curated selection for you",
    fabric: "Fabric",
    drape: "Drape",
    back: "Back",
    designer: "Designer",
    perfectFit: "FIT: PERFECT",
    recalculating: "Robert recalculating…",
    validatedBy: "Validated by Jules engine — Divineo Glow",
    collection: "Lafayette Collection",
    phaseCalibration: "Calibration",
    phaseAnalysis: "Silhouette analysis",
    phaseMaterializing: "Materializing garment",
    phaseReady: "Projection ready",
    faceCamera: "Face the camera, about 1.5 m away",
  },
  es: {
    brand: "TRYONYOU",
    patent: "Patente PCT/EP2025/067317",
    permissionTitle: "Activar la cámara",
    permissionLede: "Para proyectar la prenda sobre tu silueta en tiempo real, TRYONYOU necesita acceso a la cámara. No se guarda ninguna imagen.",
    permissionCTA: "Activar la cámara",
    permissionDenied: "Acceso a la cámara denegado. Permite el acceso en los ajustes del navegador.",
    scanning: "Escaneo biométrico en curso…",
    measuring: "Detección del cuerpo en curso…",
    bodyDetected: "Cuerpo detectado. Comparando con la base de datos…",
    fitOptimal: "Ajuste óptimo — Proyección autorizada",
    fitRecalc: "Robert recalcula el drapeado…",
    reserveCabin: "Reservar Probador",
    showMore: "Ver más",
    curated: "Selección curada para ti",
    fabric: "Tejido",
    drape: "Caída",
    back: "Volver",
    designer: "Diseñador",
    perfectFit: "AJUSTE: PERFECTO",
    recalculating: "Robert recalcula…",
    validatedBy: "Validado por el motor Jules — Divineo Glow",
    collection: "Colección Lafayette",
    phaseCalibration: "Calibración",
    phaseAnalysis: "Análisis de silueta",
    phaseMaterializing: "Materializando la prenda",
    phaseReady: "Proyección lista",
    faceCamera: "Sitúate frente a la cámara, a 1,5 m",
  },
};
