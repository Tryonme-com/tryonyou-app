"""
Sube el códice JSON (p. ej. contrato_master_v10) a Google Cloud Storage.

Credenciales: define GOOGLE_APPLICATION_CREDENTIALS (ruta al JSON de service account)
o usa Application Default Credentials (gcloud auth application-default login).

Variables de entorno:
  GCP_PROJECT_ID o GOOGLE_CLOUD_PROJECT — proyecto GCP
  GCS_BUCKET_NAME — bucket (default: tryonyou-v10-config)
  GCS_OBJECT_NAME — objeto destino (default: config_maestra.json)
  GCS_SOURCE_JSON — ruta al JSON local (default: contrato_master_v10.json junto al script)
  GCS_LOCATION — región al crear bucket (default: EU)
  GCS_MAKE_PUBLIC=1 — hace el objeto legible públicamente (por defecto NO; revisa riesgo)

  pip install google-cloud-storage
  python3 despliegue_gcs_soberano_v10.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _root_dir() -> Path:
    return Path(__file__).resolve().parent


def subir_codice_v10() -> int:
    project = (
        os.environ.get("GCP_PROJECT_ID", "").strip()
        or os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    )
    if not project:
        print(
            "❌ Define GCP_PROJECT_ID o GOOGLE_CLOUD_PROJECT.",
            file=sys.stderr,
        )
        return 1

    bucket_name = os.environ.get("GCS_BUCKET_NAME", "tryonyou-v10-config").strip()
    object_name = os.environ.get("GCS_OBJECT_NAME", "config_maestra.json").strip()
    source = Path(
        os.environ.get("GCS_SOURCE_JSON", "").strip()
        or _root_dir() / "contrato_master_v10.json"
    ).resolve()

    if not source.is_file():
        print(f"❌ No existe el archivo fuente: {source}", file=sys.stderr)
        return 1

    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not creds:
        print(
            "ℹ️  GOOGLE_APPLICATION_CREDENTIALS no definido; se usan ADC si existen.",
        )

    print("📡 Despliegue V10 → Google Cloud Storage…")

    try:
        from google.cloud import storage
    except ImportError:
        print(
            "❌ pip install google-cloud-storage",
            file=sys.stderr,
        )
        return 1

    try:
        codice_data = json.loads(source.read_text(encoding="utf-8"))
        body = json.dumps(codice_data, indent=2, ensure_ascii=False)

        client = storage.Client(project=project)
        bucket = client.bucket(bucket_name)

        if not bucket.exists():
            create_flag = os.environ.get("GCS_CREATE_BUCKET", "").strip().lower()
            if create_flag not in ("1", "true", "yes"):
                print(
                    f"❌ El bucket {bucket_name!r} no existe. "
                    "Créalo previamente o establece GCS_CREATE_BUCKET=1 "
                    "para permitir su creación automática.",
                    file=sys.stderr,
                )
                return 1
            loc = os.environ.get("GCS_LOCATION", "EU").strip() or "EU"
            bucket = client.create_bucket(bucket_name, location=loc)
            print(f"✅ Bucket {bucket_name!r} creado (location={loc!r}).")

        blob = bucket.blob(object_name)
        blob.upload_from_string(
            body, content_type="application/json; charset=utf-8"
        )

        if os.environ.get("GCS_MAKE_PUBLIC", "").strip() in (
            "1",
            "true",
            "yes",
        ):
            blob.make_public()
            print(f"\n✅ Códice subido (público): {blob.public_url}")
        else:
            gs_uri = f"gs://{bucket_name}/{object_name}"
            print(f"\n✅ Códice subido (privado): {gs_uri}")
            print(
                "ℹ️  Para URL pública: GCS_MAKE_PUBLIC=1 "
                "(valorar exposición de datos).",
            )

        return 0
    except Exception as e:
        print(f"❌ Error en el despliegue: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(subir_codice_v10())
