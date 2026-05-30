# Firebase Studio (Project IDX) — dev environment configuration
# https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  channel = "stable-24.11";

  packages = [
    pkgs.nodejs_20
    pkgs.corepack_22
    pkgs.python312
    pkgs.python312Packages.pip
    pkgs.python312Packages.virtualenv
  ];

  # ── Environment variables ──────────────────────────────────────────────────
  # Set real values in the IDX UI: Settings → Environment Variables
  # (never commit actual secrets here)
  env = {
    # ── Backend — Flask API ──────────────────────────────────────────────────
    STRIPE_ENDPOINT_SECRET        = "";
    GEMINI_API_KEY                = "";
    GMAIL_CLIENT_ID               = "";
    GMAIL_CLIENT_SECRET           = "";
    GMAIL_REFRESH_TOKEN           = "";
    GOOGLE_SERVICE_ACCOUNT_JSON   = "";
    JULES_CRON_TOKEN              = "";
    PENNYLANE_API_KEY             = "";
    SPREADSHEET_ID                = "";
    PAU_TTS_ENDPOINT              = "";
    PAU_TTS_FALLBACK_AUDIO_URL    = "";
    LAFAYETTE_VERIFY_BASE_URL     = "";
    MAX_ENVIOS_DIARIOS            = "50";
    TRYONYOU_DB_PATH              = "/tmp/tryonyou_leads.sqlite";

    # ── Frontend — Vite client ───────────────────────────────────────────────
    VITE_OAUTH_PORTAL_URL         = "";
    VITE_APP_ID                   = "";
    VITE_FRONTEND_FORGE_API_KEY   = "";
    VITE_FRONTEND_FORGE_API_URL   = "";
    VITE_ANALYTICS_ENDPOINT       = "";
    VITE_ANALYTICS_WEBSITE_ID     = "";
  };

  idx = {
    extensions = [
      "vscodevim.vim"
      "esbenp.prettier-vscode"
      "bradlc.vscode-tailwindcss"
      "ms-python.python"
      "ms-python.vscode-pylance"
    ];

    workspace = {
      onCreate = {
        install-frontend = "corepack enable && pnpm install --frozen-lockfile=false";
        install-api = ''
          python3 -m venv api/.venv
          api/.venv/bin/pip install -r api/requirements.txt
        '';
      };
      onStart = {
        run-frontend = "pnpm run dev";
        run-api = ''
          cd api && ../.venv/bin/python index.py
        '';
      };
    };

    previews = {
      enable = true;
      previews = {
        web = {
          command = ["pnpm" "run" "dev" "--" "--port" "$PORT" "--host" "0.0.0.0"];
          manager = "web";
        };
      };
    };
  };
}
