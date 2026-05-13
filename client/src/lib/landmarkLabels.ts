/**
 * TRYONYOU — landmarkLabels.ts
 * Étiquettes anatomiques françaises des 33 landmarks MediaPipe Pose,
 * regroupés en cinq chapitres pour l'overlay éditorial.
 */

export interface LandmarkChapter {
  id: string;
  title: string;
  range: [number, number];   // indices inclus
  description: string;
  labels: string[];          // une étiquette par index dans la plage
}

export const LANDMARK_CHAPTERS: LandmarkChapter[] = [
  {
    id: "visage",
    title: "Visage",
    range: [0, 10],
    description: "Yeux, nez, oreilles, bouche",
    labels: [
      "Nez",
      "Œil gauche (intérieur)",
      "Œil gauche",
      "Œil gauche (extérieur)",
      "Œil droit (intérieur)",
      "Œil droit",
      "Œil droit (extérieur)",
      "Oreille gauche",
      "Oreille droite",
      "Bouche (gauche)",
      "Bouche (droite)",
    ],
  },
  {
    id: "epaules",
    title: "Épaules",
    range: [11, 12],
    description: "Ancrage principal",
    labels: ["Épaule gauche", "Épaule droite"],
  },
  {
    id: "bras",
    title: "Bras & mains",
    range: [13, 22],
    description: "Coudes, poignets, doigts",
    labels: [
      "Coude gauche",
      "Coude droit",
      "Poignet gauche",
      "Poignet droit",
      "Auriculaire gauche",
      "Auriculaire droit",
      "Index gauche",
      "Index droit",
      "Pouce gauche",
      "Pouce droit",
    ],
  },
  {
    id: "hanches",
    title: "Hanches",
    range: [23, 24],
    description: "Point de pivot",
    labels: ["Hanche gauche", "Hanche droite"],
  },
  {
    id: "jambes",
    title: "Jambes & pieds",
    range: [25, 32],
    description: "Genoux, chevilles, talons, orteils",
    labels: [
      "Genou gauche",
      "Genou droit",
      "Cheville gauche",
      "Cheville droite",
      "Talon gauche",
      "Talon droit",
      "Orteils gauches",
      "Orteils droits",
    ],
  },
];

/** Renvoie l'étiquette française d'un landmark donné. */
export function getLandmarkLabel(idx: number): string {
  for (const ch of LANDMARK_CHAPTERS) {
    const [lo, hi] = ch.range;
    if (idx >= lo && idx <= hi) {
      return ch.labels[idx - lo] ?? `Point ${idx}`;
    }
  }
  return `Point ${idx}`;
}
