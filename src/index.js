// Filtro de tranquilidad: Solo procesa si los datos son perfectos
app.command('/cobrar', async ({ command, ack, say }) => {
  await ack();

  const amount = Number.parseFloat(command.text);

  // Si meten basura, el bot los corrige solo sin avisarte
  if (!Number.isFinite(amount) || amount <= 0) {
    return await say(
      '⚠️ Introduce un importe válido. No me hagas perder el tiempo (ni a mi jefe).'
    );
  }

  // TODO: Implementar la lógica de cobro automática.
});
