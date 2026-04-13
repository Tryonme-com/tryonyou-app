/**
 * Agent #50 — GitHub Commit Agent
 * Automatiza commits y gestión de ramas para CI/CD.
 */

export function formatSuperCommit({ version, modules, description }) {
  const emoji = "🔥";
  const lines = [
    `${emoji} TRYONYOU ${version}: ${description}`,
    "",
    ...modules.map((m) => `✅ ${m}`),
    "",
    `🌐 Destino: tryonyou.app`,
    `📋 Patente: PCT/EP2025/067317`,
  ];
  return lines.join("\n");
}

export function validateBranchName(branch) {
  const valid = /^[a-zA-Z0-9\-_/]+$/.test(branch);
  return { branch, valid, suggestion: valid ? branch : branch.replace(/[^a-zA-Z0-9\-_/]/g, "-") };
}

export default { formatSuperCommit, validateBranchName };
