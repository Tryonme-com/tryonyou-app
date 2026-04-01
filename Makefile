# =============================================================================
# TryOnYou — Makefile
# Requires: vercel CLI, node, SLACK_WEBHOOK_URL in environment
# =============================================================================

.PHONY: deploy-prod audit-slack

## deploy-prod: Build & deploy to Vercel production, then run npm audit → Slack
deploy-prod:
	@echo "🚀  Deploying to Vercel production…"
	vercel --prod
	@echo "🔒  Running post-deploy security audit…"
	node scripts/post-deploy-audit.mjs

## audit-slack: Run npm audit and send the report to Slack (standalone)
audit-slack:
	@echo "🔒  Running npm audit → Slack…"
	node scripts/post-deploy-audit.mjs
