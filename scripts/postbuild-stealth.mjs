/**
 * If BUNKER_STEALTH_TOTAL is set, replace dist/index.html with static stealth shell
 * (Vercel serves dist before Python for "/").
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");
const flag = (process.env.BUNKER_STEALTH_TOTAL || "").trim().toLowerCase();
if (!["1", "true", "yes", "on"].includes(flag)) {
  process.exit(0);
}

const tpl = path.join(root, "src", "templates", "stealth_bunker.html");
const distIndex = path.join(root, "dist", "index.html");
if (!fs.existsSync(tpl)) {
  console.error("[postbuild-stealth] template missing:", tpl);
  process.exit(1);
}
if (!fs.existsSync(distIndex)) {
  console.error("[postbuild-stealth] dist/index.html missing — run vite build first");
  process.exit(1);
}
const html = fs.readFileSync(tpl, "utf8");
fs.writeFileSync(distIndex, html, "utf8");
console.log("[postbuild-stealth] dist/index.html → SACMUSEUM stealth shell");
