/**
 * Post-Deploy Security Audit → Slack
 *
 * Run after a successful `vercel --prod` to send an npm audit summary to Slack.
 * Requires SLACK_WEBHOOK_URL to be set in the environment.
 *
 * Usage (standalone):  node scripts/post-deploy-audit.mjs
 * Usage (from Makefile): called automatically by the `deploy-prod` target.
 */

import { execSync } from "child_process";
import https from "https";
import http from "http";
import { URL } from "url";

const SLACK_WEBHOOK_URL = (process.env.SLACK_WEBHOOK_URL || "").trim();
const APP_NAME = process.env.VERCEL_PROJECT_NAME || "tryonyou-app";

/** Run npm audit and return { summary, json, exitCode } */
function runAudit() {
  let raw = "";
  let exitCode = 0;
  try {
    raw = execSync("npm audit --json 2>&1", { encoding: "utf8" });
  } catch (err) {
    raw = err.stdout || err.message || "";
    exitCode = err.status ?? 1;
  }

  let parsed = null;
  try {
    parsed = JSON.parse(raw);
  } catch {
    // non-JSON output (npm < 6 or network error)
  }

  const meta = parsed?.metadata;
  const vulns = meta?.vulnerabilities ?? {};
  const total = Object.values(vulns).reduce((s, n) => s + (n ?? 0), 0);

  const lines = [
    `📦 *npm audit* — \`${APP_NAME}\``,
    `Total vulnerabilities: *${total}*`,
  ];

  const levels = ["critical", "high", "moderate", "low", "info"];
  for (const lvl of levels) {
    const count = vulns[lvl] ?? 0;
    if (count > 0) {
      const emoji =
        lvl === "critical"
          ? "🔴"
          : lvl === "high"
            ? "🟠"
            : lvl === "moderate"
              ? "🟡"
              : lvl === "low"
                ? "🔵"
                : "⚪";
      lines.push(`  ${emoji} ${lvl}: ${count}`);
    }
  }

  if (total === 0) {
    lines.push("✅ No known vulnerabilities found.");
  } else {
    lines.push(`\n> Run \`npm audit fix\` to attempt automatic fixes.`);
  }

  if (exitCode !== 0 && !parsed) {
    lines.push(`\n⚠️ audit returned non-JSON output (exit ${exitCode}):\n\`\`\`${raw.slice(0, 800)}\`\`\``);
  }

  return { summary: lines.join("\n"), exitCode };
}

/** POST a message to the Slack Incoming Webhook */
function postToSlack(text) {
  return new Promise((resolve, reject) => {
    if (!SLACK_WEBHOOK_URL) {
      console.warn("[post-deploy-audit] SLACK_WEBHOOK_URL not set — skipping Slack notification.");
      resolve(false);
      return;
    }

    const body = Buffer.from(JSON.stringify({ text }), "utf8");
    let parsedUrl;
    try {
      parsedUrl = new URL(SLACK_WEBHOOK_URL);
    } catch {
      console.error("[post-deploy-audit] Invalid SLACK_WEBHOOK_URL.");
      resolve(false);
      return;
    }

    const transport = parsedUrl.protocol === "https:" ? https : http;
    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (parsedUrl.protocol === "https:" ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": body.length,
      },
    };

    const req = transport.request(options, (res) => {
      res.resume();
      if (res.statusCode === 200) {
        console.log("[post-deploy-audit] Slack notification sent ✓");
        resolve(true);
      } else {
        console.warn(`[post-deploy-audit] Slack returned HTTP ${res.statusCode}`);
        resolve(false);
      }
    });
    req.on("error", (err) => {
      console.error("[post-deploy-audit] Slack request error:", err.message);
      reject(err);
    });
    req.setTimeout(8000, () => {
      req.destroy(new Error("timeout"));
    });
    req.write(body);
    req.end();
  });
}

async function main() {
  console.log("[post-deploy-audit] Running npm audit…");
  const { summary, exitCode } = runAudit();
  console.log(summary);
  await postToSlack(summary);
  // Always exit 0 — vulnerabilities are reported to Slack but must not block the deployment.
  void exitCode;
  process.exit(0);
}

main().catch((err) => {
  console.error("[post-deploy-audit] Fatal:", err);
  process.exit(1);
});
