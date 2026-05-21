type PauHablaResponse = {
  status: "success" | "error";
  audio_data?: string;
  duracion_animacion_ms?: number;
};

export async function hacerHablarAPau(
  textoRespuesta: string,
  idiomaUsuario: string,
): Promise<void> {
  const avatarImg = document.getElementById(
    "pau-avatar-esquina",
  ) as HTMLImageElement | null;

  const response = await fetch("/api/pau-habla", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto: textoRespuesta, idioma: idiomaUsuario }),
  });

  const data = (await response.json()) as PauHablaResponse;
  if (data.status !== "success" || !data.audio_data) return;

  if (avatarImg) avatarImg.src = "/assets/pau_hablando.webm";

  const audio = new Audio(data.audio_data);
  await audio.play();

  const restoreAvatar = () => {
    if (avatarImg) avatarImg.src = "/assets/pau_estatico.png";
  };
  setTimeout(restoreAvatar, data.duracion_animacion_ms ?? 3000);
}
