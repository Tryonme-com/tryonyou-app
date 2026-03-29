import os
import json
import base64
from datetime import datetime


class GoogleStudioConfig:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_STUDIO_PROJECT_ID", "gen-lang-client-0091228222")
        self.client_email = os.environ.get(
            "GOOGLE_STUDIO_CLIENT_EMAIL",
            "pau-lvt-eng@google-studio.iam.gserviceaccount.com",
        )
        self.scopes = ["https://www.googleapis.com/auth/datastudio"]
        self.config_name = os.environ.get("GOOGLE_STUDIO_CONFIG_NAME", "studio_bridge_v9.json")

    def _private_key(self):
        private_key = os.environ.get("GOOGLE_STUDIO_PRIVATE_KEY", "").strip()
        private_key_b64 = os.environ.get("GOOGLE_STUDIO_PRIVATE_KEY_B64", "").strip()

        if private_key:
            return private_key
        if private_key_b64:
            return base64.b64decode(private_key_b64).decode("utf-8")
        return ""

    def generate_config_file(self):
        config_data = {
            "type": "service_account",
            "project_id": self.project_id,
            "private_key_id": os.environ.get("GOOGLE_STUDIO_PRIVATE_KEY_ID", ""),
            "private_key": self._private_key(),
            "client_email": self.client_email,
            "client_id": os.environ.get("GOOGLE_STUDIO_CLIENT_ID", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("GOOGLE_STUDIO_CERT_URL", ""),
            "scopes": self.scopes,
            "generated_at": datetime.now().isoformat(),
        }

        with open(self.config_name, "w", encoding="utf-8") as config_file:
            json.dump(config_data, config_file, indent=2)

        return config_data


if __name__ == "__main__":
    config = GoogleStudioConfig()
    generated = config.generate_config_file()
    print(json.dumps({"config_file": config.config_name, "project_id": generated["project_id"]}, indent=2))