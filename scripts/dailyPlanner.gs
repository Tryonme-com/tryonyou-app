/**
 * dailyPlanner.gs — CEO Virtual / Daily Planner
 * TryOnYou V10 · Patente PCT/EP2025/067317 · SIREN 943 610 196
 *
 * ACTIVACIÓN (una sola vez):
 *   1. Abre el editor de Apps Script: https://script.google.com
 *   2. Pega este archivo (o impórtalo desde el repo).
 *   3. Configura las propiedades del script (Archivo → Propiedades del proyecto):
 *        TELEGRAM_BOT_TOKEN  → token del bot @abvet_deploy_bot
 *        TELEGRAM_CHAT_ID    → ID numérico del chat / canal / grupo
 *   4. Ejecuta `createDailyTrigger()` UNA SOLA VEZ para instalar el disparador.
 *   5. Autoriza los permisos que solicite Google.
 *   6. El sistema enviará el informe matutino todos los días a las 09:00 AM (CET/CEST).
 *
 * Para cancelar: ejecuta `deleteDailyTrigger()`.
 */

// ─────────────────────────────────────────────────────────────────────────────
// CONSTANTES OPERATIVAS
// ─────────────────────────────────────────────────────────────────────────────

/** Nombre interno del disparador (usado para identificarlo y borrarlo). */
var TRIGGER_FUNCTION_NAME = "runDailyPlanner";

/** Hora objetivo del informe matutino (hora local configurada en el proyecto). */
var DAILY_REPORT_HOUR = 9;

/** Referencia operativa de liquidación (hito LVMH, 9 mayo 2026). */
var HITO_FECHA = new Date(2026, 4, 9); // mes 4 = mayo (0-indexed)

/** Referencia económica neta (solo para el informe). */
var NETO_REF_EUR = "98.000,00";

/** SIREN de la entidad. */
var SIREN_REF = "943 610 196";

/** Patente internacional. */
var PATENT_REF = "PCT/EP2025/067317";

// ─────────────────────────────────────────────────────────────────────────────
// GESTIÓN DEL DISPARADOR
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Instala el disparador diario a las DAILY_REPORT_HOUR:00.
 * Ejecutar UNA SOLA VEZ desde el editor de Apps Script.
 */
function createDailyTrigger() {
  // Eliminar disparadores previos con el mismo nombre para evitar duplicados.
  deleteDailyTrigger();

  ScriptApp.newTrigger(TRIGGER_FUNCTION_NAME)
    .timeBased()
    .everyDays(1)
    .atHour(DAILY_REPORT_HOUR)
    .create();

  var horaFormateada = ("0" + DAILY_REPORT_HOUR).slice(-2);
  Logger.log(
    "✅ Disparador instalado: " +
      TRIGGER_FUNCTION_NAME +
      " se ejecutará cada día a las " +
      horaFormateada +
      ":00."
  );
}

/**
 * Elimina todos los disparadores vinculados a `TRIGGER_FUNCTION_NAME`.
 * Útil para reinstalar o desactivar el planner.
 */
function deleteDailyTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  var deleted = 0;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === TRIGGER_FUNCTION_NAME) {
      ScriptApp.deleteTrigger(triggers[i]);
      deleted++;
    }
  }
  if (deleted > 0) {
    Logger.log("🗑️  " + deleted + " disparador(es) eliminado(s).");
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PUNTO DE ENTRADA PRINCIPAL (llamado por el disparador)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Función principal ejecutada cada mañana a las 09:00.
 * Orquesta la recopilación de métricas y el envío del informe al CEO virtual.
 */
function runDailyPlanner() {
  try {
    var status = getProjectStatus();
    var report = buildReport(status);
    var ok = sendTelegramReport(report);
    Logger.log(ok ? "✅ Informe enviado a Telegram." : "❌ Error al enviar informe.");
  } catch (e) {
    Logger.log("❌ runDailyPlanner: " + e.message);
    // Reintento silencioso: notificar el error también al canal.
    try {
      sendTelegramReport(
        "⚠️ *[ALERTA CEO VIRTUAL]*\n\nError en el planner matutino:\n`" +
          e.message +
          "`\n\nRevisa los logs de Apps Script."
      );
    } catch (innerErr) {
      Logger.log("❌ No se pudo enviar la alerta de error: " + innerErr.message);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// RECOPILACIÓN DE ESTADO DEL PROYECTO
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Reúne métricas clave del proyecto.
 * Amplía este objeto con llamadas a Sheets, Drive, APIs externas, etc.
 *
 * @return {Object} Objeto con los KPIs del día.
 */
function getProjectStatus() {
  var hoy = new Date();
  var diasRestantes = Math.ceil(
    (HITO_FECHA.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24)
  );

  return {
    fecha: Utilities.formatDate(hoy, "Europe/Paris", "dd/MM/yyyy HH:mm"),
    diasRestantes: diasRestantes,
    netoRef: NETO_REF_EUR,
    siren: SIREN_REF,
    patent: PATENT_REF,
    hitoLabel: "LVMH · Le Bon Marché",
    hitoFecha: Utilities.formatDate(HITO_FECHA, "Europe/Paris", "dd/MM/yyyy"),
    agentesActivos: _countActiveAgents(),
    ultimoDespliegue: _getLastDeployInfo(),
  };
}

/**
 * Devuelve el número de agentes activos registrados en el proyecto.
 * Por defecto retorna el conteo estático; extiende con una hoja de cálculo real.
 *
 * @return {number}
 */
function _countActiveAgents() {
  // Ejemplo: leer de una hoja de cálculo con ID en propiedades del script.
  var props = PropertiesService.getScriptProperties();
  var sheetId = props.getProperty("AGENTS_SHEET_ID");
  if (sheetId) {
    try {
      var ss = SpreadsheetApp.openById(sheetId);
      var sheet = ss.getSheetByName("Agentes");
      if (sheet) {
        var lastRow = sheet.getLastRow();
        return lastRow > 1 ? lastRow - 1 : 0; // restar fila de cabecera
      }
    } catch (e) {
      Logger.log("⚠️ No se pudo leer AGENTS_SHEET_ID: " + e.message);
    }
  }
  // Valor por defecto si no hay hoja configurada.
  return 7;
}

/**
 * Devuelve información sobre el último despliegue conocido.
 * Extiende con llamadas a Vercel, GitHub, GCS según tu infraestructura.
 *
 * @return {string}
 */
function _getLastDeployInfo() {
  var props = PropertiesService.getScriptProperties();
  var info = props.getProperty("LAST_DEPLOY_INFO");
  return info || "tryonyou.app · V10 Omega (ref. estática)";
}

// ─────────────────────────────────────────────────────────────────────────────
// CONSTRUCCIÓN DEL INFORME
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Construye el texto del informe matutino en formato Markdown (Telegram).
 *
 * @param {Object} status Objeto retornado por getProjectStatus().
 * @return {string} Texto del informe.
 */
function buildReport(status) {
  var hitoLinea;
  if (status.diasRestantes > 0) {
    hitoLinea =
      "⏳ Faltan *" +
      status.diasRestantes +
      " días* para el hito " +
      status.hitoLabel +
      " (" +
      status.hitoFecha +
      ").";
  } else if (status.diasRestantes === 0) {
    hitoLinea = "💰 *¡HOY ES EL DÍA!* Hito " + status.hitoLabel + " alcanzado.";
  } else {
    hitoLinea =
      "✅ Hito " +
      status.hitoLabel +
      " (" +
      status.hitoFecha +
      ") superado. Revisar estado contable.";
  }

  return (
    "🤖 *DAILY PLANNER — CEO VIRTUAL*\n" +
    "━━━━━━━━━━━━━━━━━━━━━━\n" +
    "📅 *Fecha:* " +
    status.fecha +
    " (CET)\n\n" +
    "📊 *ESTADO OPERATIVO*\n" +
    "• Agentes IA activos: *" +
    status.agentesActivos +
    "*\n" +
    "• Último despliegue: " +
    status.ultimoDespliegue +
    "\n\n" +
    "💼 *HITO ECONÓMICO*\n" +
    hitoLinea +
    "\n" +
    "💵 Capital en ruta: *" +
    status.netoRef +
    " € NETOS*\n" +
    "🏢 Entidad: SIREN " +
    status.siren +
    "\n\n" +
    "📑 Patente: " +
    status.patent +
    "\n" +
    "━━━━━━━━━━━━━━━━━━━━━━\n" +
    "_El sistema opera en modo autónomo 24/7._"
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// ENVÍO A TELEGRAM
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Envía el informe al canal de Telegram configurado.
 * Las credenciales se leen desde las Propiedades del Script (nunca en código).
 *
 * Propiedades requeridas:
 *   TELEGRAM_BOT_TOKEN  — token del bot (formato: 123456789:AAH...)
 *   TELEGRAM_CHAT_ID    — ID del chat / grupo / canal (@abvet_deploy_bot o numérico)
 *
 * @param {string} text Texto a enviar (Markdown Telegram).
 * @return {boolean} true si el envío fue exitoso.
 */
function sendTelegramReport(text) {
  var props = PropertiesService.getScriptProperties();
  var token = (props.getProperty("TELEGRAM_BOT_TOKEN") || "").trim();
  var chatId = (props.getProperty("TELEGRAM_CHAT_ID") || "").trim();

  if (!token || !chatId) {
    Logger.log(
      "❌ Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en las propiedades del script."
    );
    return false;
  }

  var url =
    "https://api.telegram.org/bot" + token + "/sendMessage";
  var payload = {
    chat_id: chatId,
    text: text,
    parse_mode: "Markdown",
  };

  var options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    var code = response.getResponseCode();
    if (code === 200) {
      return true;
    }
    Logger.log(
      "❌ Telegram HTTP " + code + ": " + response.getContentText().substring(0, 400)
    );
    return false;
  } catch (e) {
    Logger.log("❌ Telegram fetch error: " + e.message);
    return false;
  }
}
