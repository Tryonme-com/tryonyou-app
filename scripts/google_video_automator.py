#!/usr/bin/env python3
"""
Generación de vídeo (Vertex AI) y pipeline YouTube — script local.

Requisitos:
  - Vertex: proyecto con Vertex AI API, facturación, y credenciales ADC
    (export GOOGLE_APPLICATION_CREDENTIALS=/ruta/cuenta-servicio.json o gcloud auth).
  - YouTube: la subida de vídeos y commentThreads.insert exigen OAuth2 de *usuario*,
    no una API key de Data API v3. La API key solo sirve para lectura pública.

Uso:
  pip install -r scripts/requirements-google-video.txt
  python3 scripts/google_video_automator.py --prompt "..." [--dry-run]

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import argparse
import os
import sys


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def _vertex_project() -> tuple[str, str]:
    project = os.getenv("GCP_VERTEX_PROJECT_ID", "").strip()
    location = os.getenv("GCP_VERTEX_LOCATION", "us-central1").strip()
    if not project:
        print(
            "Define GCP_VERTEX_PROJECT_ID en .env (sin hardcodear en código).",
            file=sys.stderr,
        )
        sys.exit(2)
    return project, location


class GoogleVideoAutomator:
    def __init__(
        self,
        youtube_api_key: str | None = None,
        *,
        youtube_credentials_path: str | None = None,
    ) -> None:
        self._youtube_api_key = (youtube_api_key or "").strip() or None
        self._youtube_creds_path = (youtube_credentials_path or "").strip() or None
        self._youtube_ro = None
        self._youtube_rw = None
        if self._youtube_api_key:
            from googleapiclient.discovery import build

            self._youtube_ro = build("youtube", "v3", developerKey=self._youtube_api_key)

    def _youtube_rw_client(self):
        """Cliente con OAuth (subida / comentarios)."""
        if self._youtube_rw is not None:
            return self._youtube_rw
        path = self._youtube_creds_path or os.getenv("YOUTUBE_OAUTH_TOKEN_JSON", "").strip()
        if not path or not os.path.isfile(path):
            raise RuntimeError(
                "Subida y comentarios requieren OAuth. Define YOUTUBE_OAUTH_TOKEN_JSON "
                "apuntando a token.json (usuario) generado con flujo OAuth de YouTube."
            )
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        creds = Credentials.from_authorized_user_file(path, scopes)
        self._youtube_rw = build("youtube", "v3", credentials=creds)
        return self._youtube_rw

    def generate_video_vertex(self, prompt: str, output_file: str = "video_membership.mp4") -> str:
        import vertexai
        from vertexai.preview.vision_models import VideoGenerationModel

        project_id, location = _vertex_project()
        vertexai.init(project=project_id, location=location)

        model = VideoGenerationModel.from_pretrained("imagen-video-001")
        print(f"Generando vídeo con Vertex AI: {prompt}")
        video = model.generate_video(
            prompt=prompt,
            number_of_videos=1,
            fps=24,
            dimension="1024x576",
        )
        video[0].save(output_file)
        return output_file

    def upload_and_comment(
        self,
        file_path: str,
        title: str,
        description: str,
        comment_text: str,
    ) -> str:
        from googleapiclient.http import MediaFileUpload

        yt = self._youtube_rw_client()
        body = {
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "public"},
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = req.next_chunk()
            if status:
                print(f"  Subida: {int(status.progress() * 100)}%")
        video_id = response["id"]
        yt.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {"snippet": {"textOriginal": comment_text}},
                }
            },
        ).execute()
        return video_id


def main() -> None:
    _load_dotenv()
    parser = argparse.ArgumentParser(description="Vertex vídeo + YouTube (OAuth para RW)")
    parser.add_argument(
        "--prompt",
        default=os.getenv("VERTEX_VIDEO_PROMPT", "").strip()
        or "Five seconds of luxury fashion aesthetic, gold and black, cinematic soft light.",
        help="Prompt de generación (vídeo ~ estética lujo).",
    )
    parser.add_argument(
        "--output",
        default="video_membership.mp4",
        help="Ruta del MP4 generado.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No llama a Vertex ni YouTube; solo muestra configuración.",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Solo generar vídeo localmente.",
    )
    parser.add_argument(
        "--title",
        default="TryOnYou · Sovereignty",
        help="Título en YouTube.",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Descripción en YouTube.",
    )
    parser.add_argument(
        "--comment",
        default=os.getenv("YOUTUBE_MEMBERSHIP_COMMENT", "").strip(),
        help="Texto del primer comentario (p. ej. enlace membership).",
    )
    args = parser.parse_args()

    automator = GoogleVideoAutomator(
        youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
        youtube_credentials_path=os.getenv("YOUTUBE_OAUTH_TOKEN_JSON"),
    )

    if args.dry_run:
        proj, loc = _vertex_project()
        print(f"[dry-run] project={proj} location={loc}")
        print(f"[dry-run] prompt={args.prompt!r} -> {args.output}")
        print("[dry-run] Vertex/YouTube no invocados.")
        return

    out = automator.generate_video_vertex(args.prompt, output_file=args.output)
    print(f"Vídeo guardado: {out}")

    if args.skip_upload:
        print("Omitiendo YouTube (--skip-upload).")
        return

    if not args.comment:
        print(
            "Sin --comment ni YOUTUBE_MEMBERSHIP_COMMENT: no se sube a YouTube. "
            "Pasa --comment 'https://...' o define la variable.",
            file=sys.stderr,
        )
        sys.exit(3)

    vid = automator.upload_and_comment(
        out,
        title=args.title,
        description=args.description or args.prompt,
        comment_text=args.comment,
    )
    print(f"YouTube video_id={vid}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
