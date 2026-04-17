/**
 * Falla el build si falta el manifiesto Firebase del applet o el projectId no coincide.
 * Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
 */
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const path = resolve(root, "firebase-applet-config.json");
const EXPECT = "tryonyou-app";

if (!existsSync(path)) {
  console.error("[TryOnYou] Falta firebase-applet-config.json (sellado permanente).");
  process.exit(1);
}
let data;
try {
  data = JSON.parse(readFileSync(path, "utf8"));
} catch {
  console.error("[TryOnYou] firebase-applet-config.json no es JSON válido.");
  process.exit(1);
}
if (data.projectId !== EXPECT) {
  console.error(`[TryOnYou] projectId debe ser ${EXPECT}, recibido:`, data.projectId);
  process.exit(1);
}
