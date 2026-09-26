#!/usr/bin/env node

const fs = require('node:fs');
const path = require('node:path');

const rootDir = process.cwd();
const vercelPath = path.join(rootDir, 'vercel.json');
const appPath = path.join(rootDir, 'client', 'src', 'App.tsx');

const checks = [];

function readFileSafe(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return null;
  }
}

function addCheck(name, ok, detail) {
  checks.push({ name, ok, detail });
}

const vercelRaw = readFileSafe(vercelPath);
if (!vercelRaw) {
  addCheck('vercel.json existe', false, `No se encontró: ${vercelPath}`);
} else {
  let vercelConfig;
  try {
    vercelConfig = JSON.parse(vercelRaw);
  } catch (error) {
    addCheck('vercel.json válido', false, `JSON inválido: ${error.message}`);
  }

  if (vercelConfig) {
    addCheck(
      'Build Command',
      vercelConfig.buildCommand === 'npm run build',
      `Actual: ${JSON.stringify(vercelConfig.buildCommand)}`
    );

    addCheck(
      'Output Directory',
      vercelConfig.outputDirectory === 'dist',
      `Actual: ${JSON.stringify(vercelConfig.outputDirectory)}`
    );

    const framework = typeof vercelConfig.framework === 'string' ? vercelConfig.framework.toLowerCase() : '';
    addCheck(
      'Framework Preset Vite',
      framework === 'vite',
      `Actual: ${JSON.stringify(vercelConfig.framework)}`
    );
  }
}

const appRaw = readFileSafe(appPath);
if (!appRaw) {
  addCheck('client/src/App.tsx existe', false, `No se encontró: ${appPath}`);
} else {
  const importPattern = /import\s*\{\s*SmartWardrobe\s*\}\s*from\s*['"]\.\/components\/SmartWardrobe['"];?/;
  const renderPattern = /<SmartWardrobe\s*\/?>/;

  addCheck(
    'Import SmartWardrobe en App.tsx',
    importPattern.test(appRaw),
    'Se esperaba: import { SmartWardrobe } from "./components/SmartWardrobe"'
  );

  addCheck(
    'Render SmartWardrobe en App.tsx',
    renderPattern.test(appRaw),
    'Se esperaba renderizar <SmartWardrobe /> dentro de App'
  );
}

const passed = checks.filter((check) => check.ok).length;
const failed = checks.length - passed;

console.log('=== OMEGA DEPLOY AUDIT ===');
for (const check of checks) {
  console.log(`${check.ok ? '✅' : '❌'} ${check.name} — ${check.detail}`);
}

console.log(`\nResumen: ${passed}/${checks.length} checks correctos, ${failed} fallos.`);

if (failed > 0) {
  process.exitCode = 1;
} else {
  console.log('Estado: OK para despliegue según criterios OMEGA.');
}
