# bunker_sovereignty.ma
# Memory Notes — Protocolo de autonomía TryOnYou

- Bot Telegram solicitado: `@tryonyou_deploy_bot`.
- Política de seguridad: nunca incrustar tokens en código ni en repositorio; solo variables de entorno.
- Supercommit_Max operativo vía `supercommit_max.sh` con sellos obligatorios:
  - `@CertezaAbsoluta`
  - `@lo+erestu`
  - `PCT/EP2025/067317`
  - `Bajo Protocolo de Soberanía V10 - Founder: Rubén`
- Flujo soberano Agente70 endurecido:
  - Restricción explícita en respuestas 401/402/403.
  - Degradación en 5xx y payload ambiguo.
  - Fail-safe en error de sincronización.
- Validación financiera “450.000€”:
  - No se confirma automáticamente sin fuente verificable (API bancaria/ledger auditado).
  - Requiere integración explícita y evidencia transaccional firmada.
- Dossier Fatality:
  - Solo activar con orden operativa verificable y entorno controlado.
  - Evitar cambios destructivos en `main` desde automatismos.
