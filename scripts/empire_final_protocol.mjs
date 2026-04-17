import { fileURLToPath } from "node:url";

export const projectEmpire = {
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

export const ceo_engine = {
  execute(project) {
    const required = ["status", "location", "capital", "identity", "rules"];
    for (const key of required) {
      if (!(key in project)) throw new Error("falta: " + key);
    }
    if (!Array.isArray(project.rules) || !project.rules.length) {
      throw new Error("rules invalido");
    }
    const ignition_id = "IGN-" + Date.now();
    const at = new Date().toISOString();
    console.log(
      "[Empire] " + ignition_id + " " + project.identity + " @" + project.location
    );
    project.rules.forEach((r, i) => console.log("  " + (i + 1) + ". " + r));
    return { ok: true, ignition_id, project, at };
  },
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  ceo_engine.execute(projectEmpire);
}
