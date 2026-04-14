import { App } from "@slack/bolt";

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
});

// Filtro de tranquilidad: Solo procesa si los datos son perfectos
app.command("/cobrar", async ({ command, ack, say }) => {
  await ack();

  const amount = parseFloat(command.text);

  // Si meten basura, el bot los corrige solo sin avisarte
  if (!amount || amount <= 0) {
    return await say(
      "⚠️ Introduce un importe válido. No me hagas perder el tiempo (ni a mi jefe)."
    );
  }

  // Ejecución automática y silenciosa...
  // (Aquí va el resto del código del 8%)
});

(async () => {
  await app.start(process.env.PORT || 3000);
  console.log("⚡️ TryOnYou Slack bot en marcha");
})();
