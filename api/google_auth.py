import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets",
]

BASE_DIR = Path(__file__).resolve().parent
TOKEN_PATH = Path(os.environ.get("GOOGLE_TOKEN_PATH", str(BASE_DIR / "token.json")))
CLIENT_SECRET_PATH = Path(
    os.environ.get("GOOGLE_CLIENT_SECRET_PATH", str(BASE_DIR / "credentials.json"))
)


def obtener_credenciales():
    creds = None

    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except Exception:
            creds = None

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            guardar_token(creds)
            return creds
        except Exception:
            creds = None

    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if credentials_json:
        try:
            creds_data = json.loads(credentials_json)

            if creds_data.get("type") == "service_account":
                return service_account.Credentials.from_service_account_info(
                    creds_data,
                    scopes=SCOPES,
                )

            if "installed" in creds_data or "web" in creds_data:
                flow = InstalledAppFlow.from_client_config(creds_data, SCOPES)
                creds = flow.run_local_server(port=0)
                guardar_token(creds)
                return creds

        except Exception as e:
            raise RuntimeError(f"Error procesando GOOGLE_CREDENTIALS_JSON: {e}") from e

    if CLIENT_SECRET_PATH.exists():
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRET_PATH), SCOPES
        )
        creds = flow.run_local_server(port=0)
        guardar_token(creds)
        return creds

    raise RuntimeError(
        "No se encontró token.json, GOOGLE_CREDENTIALS_JSON ni credentials.json"
    )


def guardar_token(creds):
    if isinstance(creds, Credentials):
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(TOKEN_PATH), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as token:
            token.write(creds.to_json())


def obtener_servicio_sheets():
    creds = obtener_credenciales()
    return build("sheets", "v4", credentials=creds)


def obtener_servicio_gmail():
    creds = obtener_credenciales()
    return build("gmail", "v1", credentials=creds)
