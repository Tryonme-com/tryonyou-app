import type { GarmentRenderConfig } from "../lib/renderGarmentOnBody";

const CDN =
  "https://d2xsxph8kpxj0f.cloudfront.net/310519663147230146/XuPpd2FitZwzG9eMoNLmxT";

export interface DemoGarment {
  id: string;
  name: string;
  imagePath: string;
  config: GarmentRenderConfig;
}

/** Colección Elena — misma CDN que Manus Overnight (genérico, sin logos de maison). */
export const ELENA_DEMO_GARMENTS: DemoGarment[] = [
  {
    id: "robe-rouge",
    name: "Robe Rouge Elena",
    imagePath: `${CDN}/garment-robe-rouge-gRyNHjy4ZCzdiJHeg4Cpq8.png`,
    config: { shoulderWidthRatio: 0.38, neckY: 0.16, opacity: 0.9 },
  },
  {
    id: "tailleur",
    name: "Tailleur Éditorial",
    imagePath: `${CDN}/garment-tailleur-BnDoghKRgCYn6br9QbvgLF.png`,
    config: { shoulderWidthRatio: 0.4, neckY: 0.14, opacity: 0.92 },
  },
  {
    id: "gala",
    name: "Gala Elena",
    imagePath: `${CDN}/garment-gala-6k7vn4cvcqswnFo5BeQySx.png`,
    config: { shoulderWidthRatio: 0.36, neckY: 0.17, opacity: 0.88 },
  },
  {
    id: "manteau",
    name: "Manteau Cachemire",
    imagePath: `${CDN}/garment-manteau-aqkZnxu2GSiFezJY3mhuiA.png`,
    config: { shoulderWidthRatio: 0.42, neckY: 0.11, opacity: 0.93 },
  },
  {
    id: "blazer",
    name: "Blazer Divineo V11",
    imagePath: `${CDN}/garment-blazer-divineo-a39ipb93xJBVoaFoM3rcY6.png`,
    config: { shoulderWidthRatio: 0.39, neckY: 0.15, opacity: 0.9 },
  },
];
