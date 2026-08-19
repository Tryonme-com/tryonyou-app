import { copyFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import path from "node:path";

const rootDirectory = path.resolve(import.meta.dirname, "..");
const source = path.join(
  rootDirectory,
  "STATION_T",
  "PRESENTATION",
  "TRYONYOU_StationT_Presentation.pdf",
);
const destinationDirectory = path.join(
  rootDirectory,
  "public",
  "STATION_T",
  "PRESENTATION",
);
const destination = path.join(destinationDirectory, path.basename(source));

mkdirSync(destinationDirectory, { recursive: true });
rmSync(destination, { force: true });

if (!existsSync(source)) {
  console.warn(
    "[station-t] Presentation not found; static copy skipped. Add STATION_T/PRESENTATION/TRYONYOU_StationT_Presentation.pdf before deployment.",
  );
  process.exit(0);
}

copyFileSync(source, destination);
console.log(`[station-t] Presentation published at ${path.relative(rootDirectory, destination)}`);
