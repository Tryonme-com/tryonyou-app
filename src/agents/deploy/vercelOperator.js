/**
 * Agent #51 — Vercel Operator
 * Monitoriza y gestiona despliegues en Vercel.
 */

const VERCEL_STATES = {
  READY: "READY",
  BUILDING: "BUILDING",
  ERROR: "ERROR",
  QUEUED: "QUEUED",
  CANCELED: "CANCELED",
};

export function checkDeploymentHealth(deployment) {
  if (!deployment) return { healthy: false, reason: "No deployment data" };

  return {
    healthy: deployment.state === VERCEL_STATES.READY,
    state: deployment.state,
    url: deployment.url,
    createdAt: deployment.createdAt,
    buildTime: deployment.buildTime || null,
    domain: "tryonyou.app",
  };
}

export function generateVercelConfig({ framework = "vite", buildCommand, outputDir }) {
  return {
    framework,
    buildCommand: buildCommand || "npm run build",
    outputDirectory: outputDir || "dist",
    rewrites: [{ source: "/(.*)", destination: "/index.html" }],
    headers: [
      {
        source: "/assets/(.*)",
        headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
      },
    ],
  };
}

export { VERCEL_STATES };
export default { checkDeploymentHealth, generateVercelConfig, VERCEL_STATES };
