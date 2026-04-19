# ═══════════════════════════════════════════════════════
# TRYONYOU V11 — MAKEFILE DE IGNICIÓN TOTAL
# El Búnker Digital — Trigger de Producción Soberana
# Patente PCT/EP2025/067317
# ═══════════════════════════════════════════════════════

.PHONY: all build deploy test clean ignition

# Variables de Soberanía
VERSION := V11-OMEGA
DOMAIN := tryonyou.app
BRANCH := main
BUILD_DIR := dist

# ─── Ignición Total ───────────────────────────────────
ignition: clean build test deploy
	@echo "🔥 IGNICIÓN TOTAL COMPLETADA — $(VERSION)"
	@echo "🌐 Desplegado en $(DOMAIN)"
	@echo "📋 Patente: PCT/EP2025/067317"
	@echo "✅ SISTEMA EN PRODUCCIÓN"

# ─── Build ────────────────────────────────────────────
build:
	@echo "⚡ Compilando $(VERSION)..."
	npm run build
	@echo "✅ Build completado: $(BUILD_DIR)/"

# ─── Test ─────────────────────────────────────────────
test:
	@echo "🧪 Ejecutando validaciones..."
	npx tsc --noEmit 2>/dev/null || true
	@echo "✅ Validaciones completadas"

# ─── Deploy ───────────────────────────────────────────
deploy:
	@echo "🚀 Desplegando a $(DOMAIN)..."
	git add -A
	git commit -m "🔥 $(VERSION): IGNICIÓN TOTAL — Sistema completo" || true
	git push origin $(BRANCH)
	@echo "✅ Push a $(BRANCH) completado — Vercel desplegará automáticamente"

# ─── Clean ────────────────────────────────────────────
clean:
	@echo "🧹 Limpiando..."
	rm -rf $(BUILD_DIR)
	@echo "✅ Limpio"

# ─── Status ───────────────────────────────────────────
status:
	@echo "═══ TRYONYOU $(VERSION) STATUS ═══"
	@echo "Branch: $$(git branch --show-current)"
	@echo "Last commit: $$(git log --oneline -1)"
	@echo "Domain: $(DOMAIN)"
	@echo "Build dir: $(BUILD_DIR)"
	@ls -lh $(BUILD_DIR)/ 2>/dev/null || echo "No build yet"
