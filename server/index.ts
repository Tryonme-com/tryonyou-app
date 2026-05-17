import express from "express";
import { createServer } from "http";
import path from "path";
import { fileURLToPath } from "url";
import {
  startSyncCron,
  stopSyncCron,
  syncLinearToGoogleSheets,
} from "./linearSheetsSync";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const server = createServer(app);

  app.use(express.json());

  app.post("/sync", async (_req, res) => {
    const result = await syncLinearToGoogleSheets();
    const statusByResult: Record<typeof result.status, number> = {
      success: 200,
      skipped: 503,
      error: 500,
    };

    res.status(statusByResult[result.status]).json(result);
  });

  // Serve static files from dist/public in production
  const staticPath =
    process.env.NODE_ENV === "production"
      ? path.resolve(__dirname, "public")
      : path.resolve(__dirname, "..", "dist", "public");

  app.use(express.static(staticPath));

  // Handle client-side routing - serve index.html for all routes
  app.get("*", (_req, res) => {
    res.sendFile(path.join(staticPath, "index.html"));
  });

  const port = process.env.PORT || 3000;

  startSyncCron();

  const shutdown = () => {
    stopSyncCron();
    server.close((error) => {
      if (error) {
        console.error("Error while closing server", error);
        process.exit(1);
      }

      process.exit(0);
    });
  };

  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
