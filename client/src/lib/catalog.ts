/**
 * TRYONYOU — Catalogue Lafayette ×6 Designers
 * 60 vêtements · 55 tissus techniques · Brevet PCT/EP2025/067317
 *
 * Source: tryonyou.org bundle (extrait + nettoyé).
 * Les overlays sont générés procéduralement par garmentOverlays.ts
 * (silhouettes SVG or sur fond noir, alignées sur les landmarks MediaPipe).
 */

export type Fabric = {
  drapeCoefficient: number;
  weightGSM: number;
  elasticityPct: number;
  recoveryPct: number;
  frictionCoefficient: number;
  maxStrainPct: number;
  breathability: number;
  composition: string;
};

export type Garment = {
  id: string;
  ref: string;
  sku: string;
  name: string;
  designer: string;
  type: string;
  fabricKey: string;
  fabricName: string;
  price: number;
  tags: string[];
  measurements: {
    shoulderCm: number;
    chestCm: number;
    waistCm: number;
    hipCm: number;
    lengthCm: number;
  };
  isHero: boolean;
  collection: string;
};

export const FABRICS: Record<string, Fabric> = {
  "silkElastic": {
    "drapeCoefficient": 0.92,
    "weightGSM": 85,
    "elasticityPct": 12,
    "recoveryPct": 88,
    "frictionCoefficient": 0.28,
    "maxStrainPct": 18,
    "breathability": 0.75,
    "composition": "92% Silk, 8% Elastane"
  },
  "lightWool": {
    "drapeCoefficient": 0.55,
    "weightGSM": 220,
    "elasticityPct": 5,
    "recoveryPct": 72,
    "frictionCoefficient": 0.45,
    "maxStrainPct": 8,
    "breathability": 0.62,
    "composition": "100% Merino Wool"
  },
  "liquidVelvet": {
    "drapeCoefficient": 0.78,
    "weightGSM": 340,
    "elasticityPct": 8,
    "recoveryPct": 65,
    "frictionCoefficient": 0.62,
    "maxStrainPct": 14,
    "breathability": 0.35,
    "composition": "82% Viscose, 18% Silk"
  },
  "premiumCotton": {
    "drapeCoefficient": 0.48,
    "weightGSM": 180,
    "elasticityPct": 4,
    "recoveryPct": 45,
    "frictionCoefficient": 0.52,
    "maxStrainPct": 6,
    "breathability": 0.88,
    "composition": "100% Egyptian Cotton"
  },
  "industrialMix": {
    "drapeCoefficient": 0.42,
    "weightGSM": 195,
    "elasticityPct": 15,
    "recoveryPct": 92,
    "frictionCoefficient": 0.38,
    "maxStrainPct": 25,
    "breathability": 0.55,
    "composition": "60% Polyester, 30% Cotton, 10% Elastane"
  },
  "silkChiffon": {
    "drapeCoefficient": 0.96,
    "weightGSM": 45,
    "elasticityPct": 3,
    "recoveryPct": 35,
    "frictionCoefficient": 0.18,
    "maxStrainPct": 7,
    "breathability": 0.92,
    "composition": "100% Silk Chiffon"
  },
  "silkSatin": {
    "drapeCoefficient": 0.88,
    "weightGSM": 95,
    "elasticityPct": 6,
    "recoveryPct": 55,
    "frictionCoefficient": 0.15,
    "maxStrainPct": 10,
    "breathability": 0.68,
    "composition": "100% Mulberry Silk Satin"
  },
  "silkOrganza": {
    "drapeCoefficient": 0.25,
    "weightGSM": 35,
    "elasticityPct": 2,
    "recoveryPct": 30,
    "frictionCoefficient": 0.22,
    "maxStrainPct": 5,
    "breathability": 0.95,
    "composition": "100% Silk Organza"
  },
  "silkCrepe": {
    "drapeCoefficient": 0.82,
    "weightGSM": 110,
    "elasticityPct": 7,
    "recoveryPct": 60,
    "frictionCoefficient": 0.35,
    "maxStrainPct": 12,
    "breathability": 0.72,
    "composition": "100% Silk Crêpe de Chine"
  },
  "silkTwill": {
    "drapeCoefficient": 0.7,
    "weightGSM": 120,
    "elasticityPct": 4,
    "recoveryPct": 50,
    "frictionCoefficient": 0.3,
    "maxStrainPct": 8,
    "breathability": 0.7,
    "composition": "100% Silk Twill"
  },
  "woolCashmere": {
    "drapeCoefficient": 0.65,
    "weightGSM": 260,
    "elasticityPct": 8,
    "recoveryPct": 78,
    "frictionCoefficient": 0.48,
    "maxStrainPct": 12,
    "breathability": 0.58,
    "composition": "70% Wool, 30% Cashmere"
  },
  "woolFlannel": {
    "drapeCoefficient": 0.5,
    "weightGSM": 280,
    "elasticityPct": 3,
    "recoveryPct": 55,
    "frictionCoefficient": 0.55,
    "maxStrainPct": 6,
    "breathability": 0.52,
    "composition": "100% Wool Flannel"
  },
  "woolCrepe": {
    "drapeCoefficient": 0.62,
    "weightGSM": 240,
    "elasticityPct": 6,
    "recoveryPct": 68,
    "frictionCoefficient": 0.42,
    "maxStrainPct": 10,
    "breathability": 0.6,
    "composition": "95% Wool, 5% Elastane"
  },
  "woolGabardine": {
    "drapeCoefficient": 0.35,
    "weightGSM": 300,
    "elasticityPct": 3,
    "recoveryPct": 42,
    "frictionCoefficient": 0.5,
    "maxStrainPct": 5,
    "breathability": 0.48,
    "composition": "100% Worsted Wool"
  },
  "cottonPoplin": {
    "drapeCoefficient": 0.4,
    "weightGSM": 130,
    "elasticityPct": 2,
    "recoveryPct": 35,
    "frictionCoefficient": 0.55,
    "maxStrainPct": 4,
    "breathability": 0.9,
    "composition": "100% Cotton Poplin"
  },
  "cottonSateen": {
    "drapeCoefficient": 0.52,
    "weightGSM": 160,
    "elasticityPct": 3,
    "recoveryPct": 40,
    "frictionCoefficient": 0.25,
    "maxStrainPct": 5,
    "breathability": 0.82,
    "composition": "100% Cotton Sateen"
  },
  "cottonVoile": {
    "drapeCoefficient": 0.75,
    "weightGSM": 65,
    "elasticityPct": 2,
    "recoveryPct": 30,
    "frictionCoefficient": 0.32,
    "maxStrainPct": 4,
    "breathability": 0.95,
    "composition": "100% Cotton Voile"
  },
  "cottonDenim": {
    "drapeCoefficient": 0.22,
    "weightGSM": 380,
    "elasticityPct": 2,
    "recoveryPct": 25,
    "frictionCoefficient": 0.65,
    "maxStrainPct": 4,
    "breathability": 0.45,
    "composition": "100% Cotton Denim"
  },
  "linenPure": {
    "drapeCoefficient": 0.55,
    "weightGSM": 190,
    "elasticityPct": 2,
    "recoveryPct": 20,
    "frictionCoefficient": 0.48,
    "maxStrainPct": 3,
    "breathability": 0.92,
    "composition": "100% European Linen"
  },
  "linenSilk": {
    "drapeCoefficient": 0.68,
    "weightGSM": 140,
    "elasticityPct": 4,
    "recoveryPct": 45,
    "frictionCoefficient": 0.35,
    "maxStrainPct": 7,
    "breathability": 0.85,
    "composition": "60% Linen, 40% Silk"
  },
  "velvetSilk": {
    "drapeCoefficient": 0.72,
    "weightGSM": 320,
    "elasticityPct": 5,
    "recoveryPct": 55,
    "frictionCoefficient": 0.7,
    "maxStrainPct": 9,
    "breathability": 0.3,
    "composition": "100% Silk Velvet"
  },
  "velvetCotton": {
    "drapeCoefficient": 0.58,
    "weightGSM": 350,
    "elasticityPct": 4,
    "recoveryPct": 45,
    "frictionCoefficient": 0.72,
    "maxStrainPct": 7,
    "breathability": 0.38,
    "composition": "100% Cotton Velvet"
  },
  "taffetaSilk": {
    "drapeCoefficient": 0.3,
    "weightGSM": 100,
    "elasticityPct": 1,
    "recoveryPct": 25,
    "frictionCoefficient": 0.2,
    "maxStrainPct": 3,
    "breathability": 0.55,
    "composition": "100% Silk Taffeta"
  },
  "brocadeSilk": {
    "drapeCoefficient": 0.32,
    "weightGSM": 310,
    "elasticityPct": 2,
    "recoveryPct": 30,
    "frictionCoefficient": 0.4,
    "maxStrainPct": 4,
    "breathability": 0.35,
    "composition": "85% Silk, 15% Metallic Thread"
  },
  "jerseyMilano": {
    "drapeCoefficient": 0.72,
    "weightGSM": 250,
    "elasticityPct": 25,
    "recoveryPct": 95,
    "frictionCoefficient": 0.42,
    "maxStrainPct": 35,
    "breathability": 0.6,
    "composition": "70% Viscose, 25% Polyamide, 5% Elastane"
  },
  "jerseyPonte": {
    "drapeCoefficient": 0.58,
    "weightGSM": 280,
    "elasticityPct": 20,
    "recoveryPct": 90,
    "frictionCoefficient": 0.45,
    "maxStrainPct": 30,
    "breathability": 0.55,
    "composition": "65% Viscose, 30% Nylon, 5% Elastane"
  },
  "jerseySilk": {
    "drapeCoefficient": 0.9,
    "weightGSM": 120,
    "elasticityPct": 18,
    "recoveryPct": 82,
    "frictionCoefficient": 0.25,
    "maxStrainPct": 28,
    "breathability": 0.78,
    "composition": "92% Silk, 8% Elastane"
  },
  "neopreneTech": {
    "drapeCoefficient": 0.15,
    "weightGSM": 350,
    "elasticityPct": 30,
    "recoveryPct": 98,
    "frictionCoefficient": 0.55,
    "maxStrainPct": 45,
    "breathability": 0.15,
    "composition": "100% Technical Neoprene"
  },
  "laceFrench": {
    "drapeCoefficient": 0.85,
    "weightGSM": 55,
    "elasticityPct": 10,
    "recoveryPct": 70,
    "frictionCoefficient": 0.3,
    "maxStrainPct": 18,
    "breathability": 0.98,
    "composition": "80% Cotton, 20% Polyamide Lace"
  },
  "laceChantilly": {
    "drapeCoefficient": 0.88,
    "weightGSM": 48,
    "elasticityPct": 8,
    "recoveryPct": 65,
    "frictionCoefficient": 0.28,
    "maxStrainPct": 15,
    "breathability": 0.97,
    "composition": "100% Silk Chantilly Lace"
  },
  "tulleIllusion": {
    "drapeCoefficient": 0.6,
    "weightGSM": 25,
    "elasticityPct": 5,
    "recoveryPct": 50,
    "frictionCoefficient": 0.15,
    "maxStrainPct": 10,
    "breathability": 0.99,
    "composition": "100% Nylon Tulle"
  },
  "duchessSatin": {
    "drapeCoefficient": 0.38,
    "weightGSM": 290,
    "elasticityPct": 2,
    "recoveryPct": 35,
    "frictionCoefficient": 0.12,
    "maxStrainPct": 4,
    "breathability": 0.4,
    "composition": "100% Silk Duchess Satin"
  },
  "mikadoSilk": {
    "drapeCoefficient": 0.28,
    "weightGSM": 270,
    "elasticityPct": 2,
    "recoveryPct": 32,
    "frictionCoefficient": 0.18,
    "maxStrainPct": 4,
    "breathability": 0.42,
    "composition": "100% Silk Mikado"
  },
  "crepeMorocain": {
    "drapeCoefficient": 0.75,
    "weightGSM": 200,
    "elasticityPct": 6,
    "recoveryPct": 62,
    "frictionCoefficient": 0.38,
    "maxStrainPct": 10,
    "breathability": 0.65,
    "composition": "100% Wool Crêpe Marocain"
  },
  "tweedBoucle": {
    "drapeCoefficient": 0.2,
    "weightGSM": 360,
    "elasticityPct": 3,
    "recoveryPct": 38,
    "frictionCoefficient": 0.68,
    "maxStrainPct": 5,
    "breathability": 0.5,
    "composition": "60% Wool, 25% Cotton, 15% Polyamide"
  },
  "tweedHarris": {
    "drapeCoefficient": 0.18,
    "weightGSM": 400,
    "elasticityPct": 2,
    "recoveryPct": 30,
    "frictionCoefficient": 0.72,
    "maxStrainPct": 4,
    "breathability": 0.55,
    "composition": "100% Virgin Wool Harris Tweed"
  },
  "mohairAlpaca": {
    "drapeCoefficient": 0.72,
    "weightGSM": 150,
    "elasticityPct": 10,
    "recoveryPct": 75,
    "frictionCoefficient": 0.55,
    "maxStrainPct": 16,
    "breathability": 0.65,
    "composition": "50% Mohair, 50% Alpaca"
  },
  "techStretch": {
    "drapeCoefficient": 0.55,
    "weightGSM": 145,
    "elasticityPct": 22,
    "recoveryPct": 96,
    "frictionCoefficient": 0.35,
    "maxStrainPct": 35,
    "breathability": 0.7,
    "composition": "72% Polyamide, 28% Elastane"
  },
  "scubaTech": {
    "drapeCoefficient": 0.22,
    "weightGSM": 310,
    "elasticityPct": 28,
    "recoveryPct": 95,
    "frictionCoefficient": 0.42,
    "maxStrainPct": 40,
    "breathability": 0.25,
    "composition": "95% Polyester, 5% Elastane Scuba"
  },
  "charmeuseSilk": {
    "drapeCoefficient": 0.94,
    "weightGSM": 80,
    "elasticityPct": 5,
    "recoveryPct": 48,
    "frictionCoefficient": 0.12,
    "maxStrainPct": 9,
    "breathability": 0.72,
    "composition": "100% Silk Charmeuse"
  },
  "georgetteSilk": {
    "drapeCoefficient": 0.9,
    "weightGSM": 55,
    "elasticityPct": 4,
    "recoveryPct": 42,
    "frictionCoefficient": 0.22,
    "maxStrainPct": 8,
    "breathability": 0.9,
    "composition": "100% Silk Georgette"
  },
  "cloqueJacquard": {
    "drapeCoefficient": 0.45,
    "weightGSM": 230,
    "elasticityPct": 6,
    "recoveryPct": 58,
    "frictionCoefficient": 0.4,
    "maxStrainPct": 10,
    "breathability": 0.5,
    "composition": "75% Polyester, 25% Silk Jacquard"
  },
  "piqueCotton": {
    "drapeCoefficient": 0.35,
    "weightGSM": 210,
    "elasticityPct": 3,
    "recoveryPct": 38,
    "frictionCoefficient": 0.58,
    "maxStrainPct": 5,
    "breathability": 0.85,
    "composition": "100% Cotton Piqué"
  },
  "failleSilk": {
    "drapeCoefficient": 0.42,
    "weightGSM": 175,
    "elasticityPct": 2,
    "recoveryPct": 35,
    "frictionCoefficient": 0.25,
    "maxStrainPct": 4,
    "breathability": 0.55,
    "composition": "100% Silk Faille"
  },
  "doubleCrepe": {
    "drapeCoefficient": 0.68,
    "weightGSM": 245,
    "elasticityPct": 8,
    "recoveryPct": 72,
    "frictionCoefficient": 0.38,
    "maxStrainPct": 13,
    "breathability": 0.58,
    "composition": "85% Acetate, 15% Silk Double Crêpe"
  },
  "leatherNappa": {
    "drapeCoefficient": 0.45,
    "weightGSM": 550,
    "elasticityPct": 15,
    "recoveryPct": 60,
    "frictionCoefficient": 0.55,
    "maxStrainPct": 22,
    "breathability": 0.15,
    "composition": "100% Lambskin Nappa Leather"
  },
  "leatherSuede": {
    "drapeCoefficient": 0.4,
    "weightGSM": 480,
    "elasticityPct": 12,
    "recoveryPct": 55,
    "frictionCoefficient": 0.75,
    "maxStrainPct": 18,
    "breathability": 0.25,
    "composition": "100% Goatskin Suede"
  },
  "veganLeather": {
    "drapeCoefficient": 0.35,
    "weightGSM": 320,
    "elasticityPct": 10,
    "recoveryPct": 70,
    "frictionCoefficient": 0.5,
    "maxStrainPct": 16,
    "breathability": 0.2,
    "composition": "100% Cactus-Based Vegan Leather"
  },
  "sequinMesh": {
    "drapeCoefficient": 0.65,
    "weightGSM": 420,
    "elasticityPct": 18,
    "recoveryPct": 80,
    "frictionCoefficient": 0.35,
    "maxStrainPct": 28,
    "breathability": 0.4,
    "composition": "80% Polyester Mesh, 20% Sequin Overlay"
  },
  "metallicLame": {
    "drapeCoefficient": 0.72,
    "weightGSM": 110,
    "elasticityPct": 3,
    "recoveryPct": 40,
    "frictionCoefficient": 0.18,
    "maxStrainPct": 6,
    "breathability": 0.3,
    "composition": "70% Polyester, 30% Metallic Lamé"
  },
  "featherTrim": {
    "drapeCoefficient": 0.95,
    "weightGSM": 40,
    "elasticityPct": 5,
    "recoveryPct": 90,
    "frictionCoefficient": 0.15,
    "maxStrainPct": 8,
    "breathability": 0.98,
    "composition": "100% Ostrich Feather on Silk Base"
  },
  "embroideredTulle": {
    "drapeCoefficient": 0.7,
    "weightGSM": 90,
    "elasticityPct": 6,
    "recoveryPct": 55,
    "frictionCoefficient": 0.32,
    "maxStrainPct": 12,
    "breathability": 0.88,
    "composition": "70% Nylon, 30% Silk Embroidered Tulle"
  },
  "lvtMedusa": {
    "drapeCoefficient": 0.38,
    "weightGSM": 330,
    "elasticityPct": 14,
    "recoveryPct": 85,
    "frictionCoefficient": 0.48,
    "maxStrainPct": 20,
    "breathability": 0.42,
    "composition": "55% Wool, 35% Silk, 10% Elastane"
  },
  "lvtFenix": {
    "drapeCoefficient": 0.42,
    "weightGSM": 380,
    "elasticityPct": 10,
    "recoveryPct": 78,
    "frictionCoefficient": 0.52,
    "maxStrainPct": 16,
    "breathability": 0.38,
    "composition": "70% Wool, 20% Cashmere, 10% Silk"
  },
  "lvtIcaro": {
    "drapeCoefficient": 0.55,
    "weightGSM": 260,
    "elasticityPct": 18,
    "recoveryPct": 92,
    "frictionCoefficient": 0.4,
    "maxStrainPct": 28,
    "breathability": 0.5,
    "composition": "60% Technical Wool, 30% Nylon, 10% Elastane"
  }
};

export const GARMENTS: Garment[] = [
  {
    "id": "eg001",
    "ref": "EG-001",
    "sku": "EG-LAF-001",
    "name": "Robe Rouge Elena",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "silkElastic",
    "fabricName": "Seda Elástica",
    "price": 890,
    "tags": [
      "hero",
      "gala",
      "silk",
      "red"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 105
    },
    "isHero": true,
    "collection": "elena_grandini"
  },
  {
    "id": "eg002",
    "ref": "EG-002",
    "sku": "EG-LAF-002",
    "name": "Tailleur Éditorial",
    "designer": "Maison Classique",
    "type": "ensemble",
    "fabricKey": "lightWool",
    "fabricName": "Lana Ligera",
    "price": 1250,
    "tags": [
      "editorial",
      "wool",
      "structured"
    ],
    "measurements": {
      "shoulderCm": 40,
      "chestCm": 92,
      "waistCm": 72,
      "hipCm": 98,
      "lengthCm": 110
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg003",
    "ref": "EG-003",
    "sku": "EG-LAF-003",
    "name": "Gala Lafayette",
    "designer": "Atelier Nuit",
    "type": "robe",
    "fabricKey": "liquidVelvet",
    "fabricName": "Terciopelo Líquido",
    "price": 1480,
    "tags": [
      "gala",
      "velvet",
      "evening"
    ],
    "measurements": {
      "shoulderCm": 39,
      "chestCm": 90,
      "waistCm": 70,
      "hipCm": 96,
      "lengthCm": 130
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg004",
    "ref": "EG-004",
    "sku": "EG-LAF-004",
    "name": "City Look Pro",
    "designer": "Urban Atelier",
    "type": "ensemble",
    "fabricKey": "premiumCotton",
    "fabricName": "Algodón Premium",
    "price": 680,
    "tags": [
      "city",
      "cotton",
      "casual"
    ],
    "measurements": {
      "shoulderCm": 41,
      "chestCm": 94,
      "waistCm": 74,
      "hipCm": 100,
      "lengthCm": 95
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg005",
    "ref": "EG-005",
    "sku": "EG-LAF-005",
    "name": "Accessoires d'Or",
    "designer": "Maison Dorée",
    "type": "accessoire",
    "fabricKey": "industrialMix",
    "fabricName": "Mix Industrial",
    "price": 420,
    "tags": [
      "accessory",
      "gold",
      "bag"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 0,
      "hipCm": 0,
      "lengthCm": 35
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg006",
    "ref": "EG-006",
    "sku": "EG-LAF-006",
    "name": "Cascade Chiffon",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "silkChiffon",
    "fabricName": "Chiffon de Soie",
    "price": 920,
    "tags": [
      "silk",
      "chiffon",
      "flowing",
      "evening"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 120
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg007",
    "ref": "EG-007",
    "sku": "EG-LAF-007",
    "name": "Lumière Satin",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "silkSatin",
    "fabricName": "Satin de Soie",
    "price": 1050,
    "tags": [
      "silk",
      "satin",
      "gala",
      "shine"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 115
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg008",
    "ref": "EG-008",
    "sku": "EG-LAF-008",
    "name": "Nuage Organza",
    "designer": "Elena Grandini",
    "type": "jupe",
    "fabricKey": "silkOrganza",
    "fabricName": "Organza de Soie",
    "price": 780,
    "tags": [
      "silk",
      "organza",
      "structured",
      "bridal"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 75
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg009",
    "ref": "EG-009",
    "sku": "EG-LAF-009",
    "name": "Crêpe de Nuit",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "silkCrepe",
    "fabricName": "Crêpe de Soie",
    "price": 960,
    "tags": [
      "silk",
      "crepe",
      "evening",
      "fluid"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 118
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg010",
    "ref": "EG-010",
    "sku": "EG-LAF-010",
    "name": "Foulard Twill",
    "designer": "Elena Grandini",
    "type": "top",
    "fabricKey": "silkTwill",
    "fabricName": "Twill de Soie",
    "price": 540,
    "tags": [
      "silk",
      "twill",
      "blouse",
      "print"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 0,
      "lengthCm": 62
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg011",
    "ref": "EG-011",
    "sku": "EG-LAF-011",
    "name": "Charmeuse Slip",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "charmeuseSilk",
    "fabricName": "Charmeuse de Soie",
    "price": 870,
    "tags": [
      "silk",
      "charmeuse",
      "slip",
      "liquid"
    ],
    "measurements": {
      "shoulderCm": 36,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 110
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg012",
    "ref": "EG-012",
    "sku": "EG-LAF-012",
    "name": "Georgette Volante",
    "designer": "Elena Grandini",
    "type": "chemise",
    "fabricKey": "georgetteSilk",
    "fabricName": "Georgette de Soie",
    "price": 620,
    "tags": [
      "silk",
      "georgette",
      "blouse",
      "ruffle"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 90,
      "waistCm": 70,
      "hipCm": 0,
      "lengthCm": 65
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg013",
    "ref": "EG-013",
    "sku": "EG-LAF-013",
    "name": "Duchesse Gala",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "duchessSatin",
    "fabricName": "Satin Duchesse",
    "price": 1680,
    "tags": [
      "silk",
      "duchess",
      "gala",
      "structured"
    ],
    "measurements": {
      "shoulderCm": 39,
      "chestCm": 90,
      "waistCm": 68,
      "hipCm": 96,
      "lengthCm": 140
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg014",
    "ref": "EG-014",
    "sku": "EG-LAF-014",
    "name": "Mikado Sculptural",
    "designer": "Elena Grandini",
    "type": "veste",
    "fabricKey": "mikadoSilk",
    "fabricName": "Mikado de Soie",
    "price": 1120,
    "tags": [
      "silk",
      "mikado",
      "structured",
      "architectural"
    ],
    "measurements": {
      "shoulderCm": 40,
      "chestCm": 92,
      "waistCm": 72,
      "hipCm": 0,
      "lengthCm": 58
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg015",
    "ref": "EG-015",
    "sku": "EG-LAF-015",
    "name": "Faille Cocktail",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "failleSilk",
    "fabricName": "Faille de Soie",
    "price": 980,
    "tags": [
      "silk",
      "faille",
      "cocktail",
      "midi"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 100
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg016",
    "ref": "EG-016",
    "sku": "EG-LAF-016",
    "name": "Cachemire Doux",
    "designer": "Maison Classique",
    "type": "manteau",
    "fabricKey": "woolCashmere",
    "fabricName": "Laine-Cachemire",
    "price": 2200,
    "tags": [
      "wool",
      "cashmere",
      "coat",
      "luxury"
    ],
    "measurements": {
      "shoulderCm": 42,
      "chestCm": 96,
      "waistCm": 80,
      "hipCm": 102,
      "lengthCm": 105
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg017",
    "ref": "EG-017",
    "sku": "EG-LAF-017",
    "name": "Flanelle Parisienne",
    "designer": "Maison Classique",
    "type": "pantalon",
    "fabricKey": "woolFlannel",
    "fabricName": "Flanelle de Laine",
    "price": 580,
    "tags": [
      "wool",
      "flannel",
      "trouser",
      "winter"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 72,
      "hipCm": 98,
      "lengthCm": 100
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg018",
    "ref": "EG-018",
    "sku": "EG-LAF-018",
    "name": "Crêpe Marocain Fluide",
    "designer": "Atelier Nuit",
    "type": "robe",
    "fabricKey": "crepeMorocain",
    "fabricName": "Crêpe Marocain",
    "price": 890,
    "tags": [
      "wool",
      "crepe",
      "morocain",
      "drape"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 115
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg019",
    "ref": "EG-019",
    "sku": "EG-LAF-019",
    "name": "Gabardine Stricte",
    "designer": "Maison Classique",
    "type": "pantalon",
    "fabricKey": "woolGabardine",
    "fabricName": "Gabardine de Laine",
    "price": 620,
    "tags": [
      "wool",
      "gabardine",
      "tailored",
      "sharp"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 74,
      "hipCm": 100,
      "lengthCm": 102
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg020",
    "ref": "EG-020",
    "sku": "EG-LAF-020",
    "name": "Crêpe Laine Souple",
    "designer": "Elena Grandini",
    "type": "jupe",
    "fabricKey": "woolCrepe",
    "fabricName": "Crêpe de Laine",
    "price": 520,
    "tags": [
      "wool",
      "crepe",
      "skirt",
      "fluid"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 70
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg021",
    "ref": "EG-021",
    "sku": "EG-LAF-021",
    "name": "Bouclé Chanel",
    "designer": "Maison Classique",
    "type": "veste",
    "fabricKey": "tweedBoucle",
    "fabricName": "Tweed Bouclé",
    "price": 1580,
    "tags": [
      "tweed",
      "boucle",
      "jacket",
      "iconic"
    ],
    "measurements": {
      "shoulderCm": 40,
      "chestCm": 92,
      "waistCm": 72,
      "hipCm": 98,
      "lengthCm": 58
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg022",
    "ref": "EG-022",
    "sku": "EG-LAF-022",
    "name": "Harris Overcoat",
    "designer": "Maison Classique",
    "type": "manteau",
    "fabricKey": "tweedHarris",
    "fabricName": "Tweed Harris",
    "price": 1890,
    "tags": [
      "tweed",
      "harris",
      "overcoat",
      "heritage"
    ],
    "measurements": {
      "shoulderCm": 44,
      "chestCm": 100,
      "waistCm": 84,
      "hipCm": 106,
      "lengthCm": 110
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg023",
    "ref": "EG-023",
    "sku": "EG-LAF-023",
    "name": "Double Crêpe Midi",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "doubleCrepe",
    "fabricName": "Double Crêpe",
    "price": 780,
    "tags": [
      "crepe",
      "double",
      "midi",
      "office"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 105
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg024",
    "ref": "EG-024",
    "sku": "EG-LAF-024",
    "name": "Mohair Nuage",
    "designer": "Atelier Nuit",
    "type": "top",
    "fabricKey": "mohairAlpaca",
    "fabricName": "Mohair-Alpaga",
    "price": 480,
    "tags": [
      "mohair",
      "alpaca",
      "knit",
      "soft"
    ],
    "measurements": {
      "shoulderCm": 40,
      "chestCm": 94,
      "waistCm": 76,
      "hipCm": 0,
      "lengthCm": 60
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg025",
    "ref": "EG-025",
    "sku": "EG-LAF-025",
    "name": "Jersey Milano Robe",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "jerseyMilano",
    "fabricName": "Jersey Milano",
    "price": 720,
    "tags": [
      "jersey",
      "milano",
      "stretch",
      "body"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 108
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg026",
    "ref": "EG-026",
    "sku": "EG-LAF-026",
    "name": "Popeline Chemise",
    "designer": "Urban Atelier",
    "type": "chemise",
    "fabricKey": "cottonPoplin",
    "fabricName": "Popeline de Coton",
    "price": 320,
    "tags": [
      "cotton",
      "poplin",
      "shirt",
      "crisp"
    ],
    "measurements": {
      "shoulderCm": 40,
      "chestCm": 92,
      "waistCm": 74,
      "hipCm": 0,
      "lengthCm": 72
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg027",
    "ref": "EG-027",
    "sku": "EG-LAF-027",
    "name": "Sateen Nocturne",
    "designer": "Atelier Nuit",
    "type": "pantalon",
    "fabricKey": "cottonSateen",
    "fabricName": "Satin de Coton",
    "price": 420,
    "tags": [
      "cotton",
      "sateen",
      "trouser",
      "sheen"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 72,
      "hipCm": 98,
      "lengthCm": 100
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg028",
    "ref": "EG-028",
    "sku": "EG-LAF-028",
    "name": "Voile Été",
    "designer": "Elena Grandini",
    "type": "chemise",
    "fabricKey": "cottonVoile",
    "fabricName": "Voile de Coton",
    "price": 280,
    "tags": [
      "cotton",
      "voile",
      "summer",
      "light"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 90,
      "waistCm": 72,
      "hipCm": 0,
      "lengthCm": 65
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg029",
    "ref": "EG-029",
    "sku": "EG-LAF-029",
    "name": "Denim Selvedge Brut",
    "designer": "Urban Atelier",
    "type": "pantalon",
    "fabricKey": "cottonDenim",
    "fabricName": "Denim Selvedge",
    "price": 380,
    "tags": [
      "denim",
      "selvedge",
      "raw",
      "jean"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 76,
      "hipCm": 100,
      "lengthCm": 104
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg030",
    "ref": "EG-030",
    "sku": "EG-LAF-030",
    "name": "Piqué Polo Luxe",
    "designer": "Urban Atelier",
    "type": "top",
    "fabricKey": "piqueCotton",
    "fabricName": "Piqué de Coton",
    "price": 260,
    "tags": [
      "cotton",
      "pique",
      "polo",
      "sport"
    ],
    "measurements": {
      "shoulderCm": 42,
      "chestCm": 96,
      "waistCm": 80,
      "hipCm": 0,
      "lengthCm": 68
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg031",
    "ref": "EG-031",
    "sku": "EG-LAF-031",
    "name": "Lin Pur Été",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "linenPure",
    "fabricName": "Lin Pur",
    "price": 580,
    "tags": [
      "linen",
      "pure",
      "summer",
      "natural"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 112
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg032",
    "ref": "EG-032",
    "sku": "EG-LAF-032",
    "name": "Lin-Soie Riviera",
    "designer": "Elena Grandini",
    "type": "combinaison",
    "fabricKey": "linenSilk",
    "fabricName": "Lin-Soie",
    "price": 820,
    "tags": [
      "linen",
      "silk",
      "jumpsuit",
      "resort"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 140
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg033",
    "ref": "EG-033",
    "sku": "EG-LAF-033",
    "name": "Denim Veste Oversize",
    "designer": "Urban Atelier",
    "type": "veste",
    "fabricKey": "cottonDenim",
    "fabricName": "Denim Selvedge",
    "price": 450,
    "tags": [
      "denim",
      "jacket",
      "oversize",
      "casual"
    ],
    "measurements": {
      "shoulderCm": 46,
      "chestCm": 104,
      "waistCm": 90,
      "hipCm": 108,
      "lengthCm": 65
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg034",
    "ref": "EG-034",
    "sku": "EG-LAF-034",
    "name": "Voile Robe Longue",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "cottonVoile",
    "fabricName": "Voile de Coton",
    "price": 480,
    "tags": [
      "cotton",
      "voile",
      "maxi",
      "summer"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 135
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg035",
    "ref": "EG-035",
    "sku": "EG-LAF-035",
    "name": "Popeline Robe Chemise",
    "designer": "Urban Atelier",
    "type": "robe",
    "fabricKey": "cottonPoplin",
    "fabricName": "Popeline de Coton",
    "price": 420,
    "tags": [
      "cotton",
      "poplin",
      "shirt-dress",
      "classic"
    ],
    "measurements": {
      "shoulderCm": 39,
      "chestCm": 90,
      "waistCm": 70,
      "hipCm": 96,
      "lengthCm": 100
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg036",
    "ref": "EG-036",
    "sku": "EG-LAF-036",
    "name": "Velours Soie Opéra",
    "designer": "Atelier Nuit",
    "type": "robe",
    "fabricKey": "velvetSilk",
    "fabricName": "Velours de Soie",
    "price": 1580,
    "tags": [
      "velvet",
      "silk",
      "opera",
      "evening"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 130
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg037",
    "ref": "EG-037",
    "sku": "EG-LAF-037",
    "name": "Velours Coton Blazer",
    "designer": "Maison Classique",
    "type": "veste",
    "fabricKey": "velvetCotton",
    "fabricName": "Velours de Coton",
    "price": 780,
    "tags": [
      "velvet",
      "cotton",
      "blazer",
      "autumn"
    ],
    "measurements": {
      "shoulderCm": 41,
      "chestCm": 94,
      "waistCm": 74,
      "hipCm": 0,
      "lengthCm": 62
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg038",
    "ref": "EG-038",
    "sku": "EG-LAF-038",
    "name": "Taffetas Gala",
    "designer": "Atelier Nuit",
    "type": "jupe",
    "fabricKey": "taffetaSilk",
    "fabricName": "Taffetas de Soie",
    "price": 680,
    "tags": [
      "taffeta",
      "silk",
      "ball",
      "volume"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 80
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg039",
    "ref": "EG-039",
    "sku": "EG-LAF-039",
    "name": "Brocart Impérial",
    "designer": "Elena Grandini",
    "type": "veste",
    "fabricKey": "brocadeSilk",
    "fabricName": "Brocart de Soie",
    "price": 1950,
    "tags": [
      "brocade",
      "silk",
      "imperial",
      "metallic"
    ],
    "measurements": {
      "shoulderCm": 40,
      "chestCm": 92,
      "waistCm": 72,
      "hipCm": 0,
      "lengthCm": 55
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg040",
    "ref": "EG-040",
    "sku": "EG-LAF-040",
    "name": "Sequin Mesh Nuit",
    "designer": "Atelier Nuit",
    "type": "top",
    "fabricKey": "sequinMesh",
    "fabricName": "Maille Pailletée",
    "price": 580,
    "tags": [
      "sequin",
      "mesh",
      "party",
      "sparkle"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 0,
      "lengthCm": 55
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg041",
    "ref": "EG-041",
    "sku": "EG-LAF-041",
    "name": "Lamé Cocktail",
    "designer": "Atelier Nuit",
    "type": "robe",
    "fabricKey": "metallicLame",
    "fabricName": "Lamé Métallique",
    "price": 920,
    "tags": [
      "lame",
      "metallic",
      "cocktail",
      "shine"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 95
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg042",
    "ref": "EG-042",
    "sku": "EG-LAF-042",
    "name": "Plume Capelet",
    "designer": "Elena Grandini",
    "type": "accessoire",
    "fabricKey": "featherTrim",
    "fabricName": "Garniture Plume",
    "price": 1200,
    "tags": [
      "feather",
      "cape",
      "evening",
      "dramatic"
    ],
    "measurements": {
      "shoulderCm": 42,
      "chestCm": 0,
      "waistCm": 0,
      "hipCm": 0,
      "lengthCm": 40
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg043",
    "ref": "EG-043",
    "sku": "EG-LAF-043",
    "name": "Dentelle Française Robe",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "laceFrench",
    "fabricName": "Dentelle Française",
    "price": 1350,
    "tags": [
      "lace",
      "french",
      "romantic",
      "bridal"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 120
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg044",
    "ref": "EG-044",
    "sku": "EG-LAF-044",
    "name": "Chantilly Noire",
    "designer": "Atelier Nuit",
    "type": "top",
    "fabricKey": "laceChantilly",
    "fabricName": "Dentelle de Chantilly",
    "price": 680,
    "tags": [
      "lace",
      "chantilly",
      "black",
      "delicate"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 0,
      "lengthCm": 58
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg045",
    "ref": "EG-045",
    "sku": "EG-LAF-045",
    "name": "Tulle Illusion Gala",
    "designer": "Elena Grandini",
    "type": "jupe",
    "fabricKey": "tulleIllusion",
    "fabricName": "Tulle Illusion",
    "price": 520,
    "tags": [
      "tulle",
      "illusion",
      "gala",
      "layered"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 85
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg046",
    "ref": "EG-046",
    "sku": "EG-LAF-046",
    "name": "Tulle Brodé Robe",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "embroideredTulle",
    "fabricName": "Tulle Brodé",
    "price": 1480,
    "tags": [
      "tulle",
      "embroidered",
      "couture",
      "evening"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 135
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg047",
    "ref": "EG-047",
    "sku": "EG-LAF-047",
    "name": "Jacquard Cloqué Veste",
    "designer": "Maison Classique",
    "type": "veste",
    "fabricKey": "cloqueJacquard",
    "fabricName": "Cloqué Jacquard",
    "price": 890,
    "tags": [
      "jacquard",
      "cloque",
      "texture",
      "structured"
    ],
    "measurements": {
      "shoulderCm": 40,
      "chestCm": 92,
      "waistCm": 72,
      "hipCm": 0,
      "lengthCm": 56
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg048",
    "ref": "EG-048",
    "sku": "EG-LAF-048",
    "name": "Dentelle Combinaison",
    "designer": "Elena Grandini",
    "type": "combinaison",
    "fabricKey": "laceFrench",
    "fabricName": "Dentelle Française",
    "price": 1580,
    "tags": [
      "lace",
      "jumpsuit",
      "evening",
      "statement"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 145
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg049",
    "ref": "EG-049",
    "sku": "EG-LAF-049",
    "name": "Néoprène Sculptural",
    "designer": "Urban Atelier",
    "type": "veste",
    "fabricKey": "neopreneTech",
    "fabricName": "Néoprène Technique",
    "price": 680,
    "tags": [
      "neoprene",
      "tech",
      "sculptural",
      "modern"
    ],
    "measurements": {
      "shoulderCm": 42,
      "chestCm": 96,
      "waistCm": 76,
      "hipCm": 0,
      "lengthCm": 55
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg050",
    "ref": "EG-050",
    "sku": "EG-LAF-050",
    "name": "Tech Stretch Pantalon",
    "designer": "Urban Atelier",
    "type": "pantalon",
    "fabricKey": "techStretch",
    "fabricName": "Tech Stretch",
    "price": 420,
    "tags": [
      "tech",
      "stretch",
      "trouser",
      "performance"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 72,
      "hipCm": 98,
      "lengthCm": 102
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg051",
    "ref": "EG-051",
    "sku": "EG-LAF-051",
    "name": "Scuba Robe Moderne",
    "designer": "Urban Atelier",
    "type": "robe",
    "fabricKey": "scubaTech",
    "fabricName": "Scuba Technique",
    "price": 580,
    "tags": [
      "scuba",
      "tech",
      "modern",
      "structured"
    ],
    "measurements": {
      "shoulderCm": 39,
      "chestCm": 90,
      "waistCm": 70,
      "hipCm": 96,
      "lengthCm": 98
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg052",
    "ref": "EG-052",
    "sku": "EG-LAF-052",
    "name": "Nappa Perfecto",
    "designer": "Urban Atelier",
    "type": "veste",
    "fabricKey": "leatherNappa",
    "fabricName": "Cuir Nappa",
    "price": 2400,
    "tags": [
      "leather",
      "nappa",
      "biker",
      "luxury"
    ],
    "measurements": {
      "shoulderCm": 42,
      "chestCm": 96,
      "waistCm": 78,
      "hipCm": 0,
      "lengthCm": 58
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg053",
    "ref": "EG-053",
    "sku": "EG-LAF-053",
    "name": "Daim Trench",
    "designer": "Maison Classique",
    "type": "manteau",
    "fabricKey": "leatherSuede",
    "fabricName": "Daim",
    "price": 2100,
    "tags": [
      "suede",
      "trench",
      "coat",
      "autumn"
    ],
    "measurements": {
      "shoulderCm": 43,
      "chestCm": 98,
      "waistCm": 80,
      "hipCm": 104,
      "lengthCm": 100
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg054",
    "ref": "EG-054",
    "sku": "EG-LAF-054",
    "name": "Cuir Végétal Moto",
    "designer": "Urban Atelier",
    "type": "veste",
    "fabricKey": "veganLeather",
    "fabricName": "Cuir Végétal",
    "price": 780,
    "tags": [
      "vegan",
      "leather",
      "moto",
      "sustainable"
    ],
    "measurements": {
      "shoulderCm": 41,
      "chestCm": 94,
      "waistCm": 74,
      "hipCm": 0,
      "lengthCm": 56
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg055",
    "ref": "EG-055",
    "sku": "EG-LAF-055",
    "name": "Ponte Roma Pantalon",
    "designer": "Urban Atelier",
    "type": "pantalon",
    "fabricKey": "jerseyPonte",
    "fabricName": "Jersey Ponte Roma",
    "price": 380,
    "tags": [
      "jersey",
      "ponte",
      "trouser",
      "comfort"
    ],
    "measurements": {
      "shoulderCm": 0,
      "chestCm": 0,
      "waistCm": 70,
      "hipCm": 96,
      "lengthCm": 100
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg056",
    "ref": "EG-056",
    "sku": "EG-LAF-056",
    "name": "Jersey Soie Drapé",
    "designer": "Elena Grandini",
    "type": "robe",
    "fabricKey": "jerseySilk",
    "fabricName": "Jersey de Soie",
    "price": 920,
    "tags": [
      "jersey",
      "silk",
      "drape",
      "goddess"
    ],
    "measurements": {
      "shoulderCm": 37,
      "chestCm": 86,
      "waistCm": 66,
      "hipCm": 92,
      "lengthCm": 125
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg057",
    "ref": "EG-057",
    "sku": "EG-LAF-057",
    "name": "Milano Ensemble",
    "designer": "Elena Grandini",
    "type": "ensemble",
    "fabricKey": "jerseyMilano",
    "fabricName": "Jersey Milano",
    "price": 860,
    "tags": [
      "jersey",
      "milano",
      "set",
      "stretch"
    ],
    "measurements": {
      "shoulderCm": 38,
      "chestCm": 88,
      "waistCm": 68,
      "hipCm": 94,
      "lengthCm": 105
    },
    "isHero": false,
    "collection": "elena_grandini"
  },
  {
    "id": "eg058",
    "ref": "EG-058",
    "sku": "LVT-MEDUSA",
    "name": "Medusa Silenciosa",
    "designer": "LVT Vogue",
    "type": "veste",
    "fabricKey": "lvtMedusa",
    "fabricName": "LVT Medusa Silenciosa",
    "price": 1800,
    "tags": [
      "lvt",
      "vogue",
      "cubist",
      "art"
    ],
    "measurements": {
      "shoulderCm": 42,
      "chestCm": 96,
      "waistCm": 78,
      "hipCm": 0,
      "lengthCm": 62
    },
    "isHero": false,
    "collection": "lvt_vogue"
  },
  {
    "id": "eg059",
    "ref": "EG-059",
    "sku": "LVT-FENIX",
    "name": "Fénix en Ruinas",
    "designer": "LVT Vogue",
    "type": "veste",
    "fabricKey": "lvtFenix",
    "fabricName": "LVT Fénix en Ruinas",
    "price": 1850,
    "tags": [
      "lvt",
      "vogue",
      "phoenix",
      "fire"
    ],
    "measurements": {
      "shoulderCm": 43,
      "chestCm": 98,
      "waistCm": 80,
      "hipCm": 0,
      "lengthCm": 65
    },
    "isHero": false,
    "collection": "lvt_vogue"
  },
  {
    "id": "eg060",
    "ref": "EG-060",
    "sku": "LVT-ICARO",
    "name": "Ícaro Roto",
    "designer": "LVT Vogue",
    "type": "veste",
    "fabricKey": "lvtIcaro",
    "fabricName": "LVT Ícaro Roto",
    "price": 1900,
    "tags": [
      "lvt",
      "vogue",
      "wings",
      "art"
    ],
    "measurements": {
      "shoulderCm": 42,
      "chestCm": 96,
      "waistCm": 76,
      "hipCm": 0,
      "lengthCm": 60
    },
    "isHero": false,
    "collection": "lvt_vogue"
  }
];

export const DESIGNERS = Array.from(new Set(GARMENTS.map((g) => g.designer))).sort();

export const COLLECTIONS = Array.from(new Set(GARMENTS.map((g) => g.collection))).sort();

export const TYPES = Array.from(new Set(GARMENTS.map((g) => g.type))).sort();

export const STATS = {
  totalGarments: GARMENTS.length,
  totalFabrics: Object.keys(FABRICS).length,
  designers: DESIGNERS,
  priceRange: {
    min: Math.min(...GARMENTS.map((g) => g.price)),
    max: Math.max(...GARMENTS.map((g) => g.price)),
  },
};

/** Curated featured items for the /tryon experience (hero-first). */
export const FEATURED: Garment[] = GARMENTS.filter((g) => g.isHero)
  .concat(GARMENTS.filter((g) => !g.isHero).slice(0, 12));

/** Lookup helpers */
export function getGarmentBySku(sku: string): Garment | undefined {
  return GARMENTS.find((g) => g.sku === sku || g.ref === sku);
}

export function getGarmentById(id: string): Garment | undefined {
  return GARMENTS.find((g) => g.id === id);
}
