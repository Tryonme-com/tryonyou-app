/**
 * Protocolo final Empire - ignicion cobro / reinversion (Node ESM).
 * Patente: PCT/EP2025/067317
 */

import { fileURLToPath } from "node:url";

const projectEmpire = {
  status: "PRODUCTION_LIVE",
  location: "LOCAL_PARIS_PROPIO",
  capital: 27500,
  identity: "PAU_SOVEREIGNTY_V11",
  rules: [
    "No cargar cajas",
    "Solo divineo real",
    "Alta sociedad SacMuseum",
    "BPI France Growth",
  ],
};

const ceo_engine = {
  execute(project) {
    const required = ["status", "location", "capital", "identity", "rules"];
    for (const key of required) {
      if (!(key in project)) {
        throw new Error("empire_final_protocol: falta campo: " + key);
      }
    }
    if (!Array.isArray(project.rules) || project.rules.length === 0) {
      throw new Error("empire_final_protocol: rules debe ser array no vacio");
    }
    const ignition_id = "IGN-" + Date.now();
    const at = new Date().toISOString();
    const payload = { ok: true, ignition_id, project, at };
    console.log(
      "[Empire] Ignicion " +
        ignition_id +
        " — " +
        project.identity +
        " @ " +
        project.location +
        " — capital ref: " +
        project.capital
    );
    project.rules.forEach((r, i) => console.log("  " + (i + 1) + ". " + r));
    return payload;
  },
};

const isMain = process.argv[1] === fileURLToPath(import.meta.url);
if (isMain) {
  ceo_engine.execute(projectEmpire);
}

export { ceo_engine, projectEmpire };
