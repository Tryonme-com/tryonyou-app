# Daily Planner — CEO Virtual: Guía de Activación

> **TryOnYou V10 · Patente PCT/EP2025/067317 · SIREN 943 610 196**

El script `scripts/dailyPlanner.gs` convierte Google Apps Script en tu **CEO Virtual autónomo**: reúne el estado del proyecto, calcula el contador de días hasta el hito LVMH y envía un informe completo a tu canal de Telegram (`@abvet_deploy_bot`) cada mañana a las **09:00 AM (CET/CEST)**, sin intervención manual.

---

## Requisitos previos

| Elemento | Dónde obtenerlo |
|---|---|
| Cuenta Google | Cualquier cuenta Gmail / Workspace |
| Bot de Telegram | `@BotFather` → `/newbot` o usa el existente `@abvet_deploy_bot` |
| Token del bot | Lo proporciona BotFather (formato `123456789:AAH…`) |
| Chat ID del canal/grupo | Usa `@userinfobot` o `https://api.telegram.org/bot<TOKEN>/getUpdates` |

---

## Pasos de Activación (una sola vez)

### 1. Abrir el editor de Apps Script

Ve a [https://script.google.com](https://script.google.com) e inicia sesión con tu cuenta Google.

### 2. Crear el proyecto

1. Haz clic en **"Nuevo proyecto"**.
2. Renómbralo: **TryOnYou Daily Planner**.

### 3. Pegar el script

1. En el editor, borra el contenido del archivo `Código.gs`.
2. Copia **todo** el contenido de `scripts/dailyPlanner.gs` y pégalo.
3. Guarda: `Ctrl + S` (o `Cmd + S`).

### 4. Configurar las credenciales (sin exponer secretos en código)

1. En el menú superior: **"Proyecto" → "Propiedades del proyecto" → pestaña "Propiedades del script"**.
2. Añade las siguientes propiedades:

| Propiedad | Valor |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token de `@abvet_deploy_bot` (formato `123456789:AAH…`) |
| `TELEGRAM_CHAT_ID` | ID numérico o `@nombre` del canal/grupo |

> **Opcional — Hoja de Agentes**
>
> Si quieres que el planner cuente agentes desde una Google Sheet:
> | Propiedad | Valor |
> |---|---|
> | `AGENTS_SHEET_ID` | ID de la hoja (en la URL: `…/spreadsheets/d/**ID**/edit`) |
>
> La hoja debe llamarse `Agentes` y tener una fila de cabecera. Cada fila adicional = 1 agente activo.

> **Opcional — Info de último despliegue**
>
> | Propiedad | Valor |
> |---|---|
> | `LAST_DEPLOY_INFO` | Texto libre, p. ej.: `tryonyou.app · V10 Omega · deploy 2026-04-04` |

3. Haz clic en **"Guardar"**.

### 5. Activar el disparador

1. En el editor, selecciona la función `createDailyTrigger` en el desplegable de funciones.
2. Haz clic en **▶ Ejecutar**.
3. Google pedirá **autorización**: acepta todos los permisos.
4. Comprueba el log: debe aparecer `✅ Disparador instalado: runDailyPlanner se ejecutará cada día a las 09:00.`

### 6. Verificar el informe

Para probar sin esperar a las 09:00:

1. Selecciona la función `runDailyPlanner`.
2. Haz clic en **▶ Ejecutar**.
3. Revisa tu Telegram: deberías recibir un mensaje del bot con el informe completo.

---

## Ejemplo de informe matutino

```
🤖 DAILY PLANNER — CEO VIRTUAL
━━━━━━━━━━━━━━━━━━━━━━
📅 Fecha: 04/04/2026 09:00 (CET)

📊 ESTADO OPERATIVO
• Agentes IA activos: 7
• Último despliegue: tryonyou.app · V10 Omega (ref. estática)

💼 HITO ECONÓMICO
⏳ Faltan 35 días para el hito LVMH · Le Bon Marché (09/05/2026).
💵 Capital en ruta: 98.000,00 € NETOS
🏢 Entidad: SIREN 943 610 196

📑 Patente: PCT/EP2025/067317
━━━━━━━━━━━━━━━━━━━━━━
El sistema opera en modo autónomo 24/7.
```

---

## Desactivar el planner

1. Selecciona la función `deleteDailyTrigger`.
2. Haz clic en **▶ Ejecutar**.
3. Log: `🗑️ 1 disparador(es) eliminado(s).`

---

## Arquitectura del script

```
dailyPlanner.gs
├── createDailyTrigger()    ← instala el disparador 09:00 AM
├── deleteDailyTrigger()    ← elimina el disparador existente
├── runDailyPlanner()       ← punto de entrada del disparador
│   ├── getProjectStatus()  ← reúne KPIs del proyecto
│   │   ├── _countActiveAgents()   ← opcional: desde Google Sheets
│   │   └── _getLastDeployInfo()   ← opcional: desde propiedades
│   ├── buildReport()       ← construye el Markdown del informe
│   └── sendTelegramReport()← envía el informe a Telegram
```

---

*Documento de activación — TryOnYou / Divineo. Bajo Protocolo de Soberanía V10.*
