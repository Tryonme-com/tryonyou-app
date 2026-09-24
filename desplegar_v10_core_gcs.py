"""
Sube v10_core_config.json a Google Cloud Storage.

  export GCP_PROJECT_ID=…
  export GOOGLE_APPLICATION_CREDENTIALS=/ruta/service-account.json
  export GCS_BUCKET_NAME=tryonyou-production-v10   # default
  export GCS_OBJECT_NAME=v10_core_config.json      # default
  export GCS_MAKE_PUBLIC=1                         # opcional (riesgo de exposición)

  pip install google-cloud-storage
  python3 desplegar_v10_core_gcs.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parent


def desplegar_configuracion() -> int:
    project = (
        os.environ.get("GCP_PROJECT_ID", "").strip()
        or os.environ.get("GOOGLE_CLOUD_PROJECT", "").strip()
    )
    if not project:
        print("❌ Define GCP_PROJECT_ID o GOOGLE_CLOUD_PROJECT.", file=sys.stderr)
        return 1

    bucket_name = os.environ.get(
        "GCS_BUCKET_NAME", "tryonyou-production-v10"
    ).strip()
    object_name = os.environ.get("GCS_OBJECT_NAME", "v10_core_config.json").strip()
    source = Path(
        os.environ.get("GCS_SOURCE_JSON", "").strip()
        or _root() / "v10_core_config.json"
    ).resolve()

    if not source.is_file():
        print(f"❌ No existe: {source}", file=sys.stderr)
        return 1

    try:
        from google.cloud import storage
    except ImportError:
        print("❌ pip install google-cloud-storage", file=sys.stderr)
        return 1

    data = json.loads(source.read_text(encoding="utf-8"))
    body = json.dumps(data, indent=2, ensure_ascii=False)

    try:
        client = storage.Client(project=project)
        bucket = client.bucket(bucket_name)

        if not bucket.exists():
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
            print(f"✅ V10 desplegada (pública): {blob.public_url}")
        else:
            print(f"✅ V10 desplegada (privada): gs://{bucket_name}/{object_name}")
            print("ℹ️  GCS_MAKE_PUBLIC=1 para URL pública (valorar riesgo).")

        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(desplegar_configuracion())
