# Firebase Studio workspace configuration
# https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  channel = "stable-24.05";

  packages = [
    pkgs.python312
    pkgs.nodejs_20
    pkgs.corepack_20
    pkgs.sqlite
  ];

  # ─── Environment variables ────────────────────────────────────────────────────
  # Copy .env.local (git-ignored) to populate these at runtime.
  # Sensitive values must never be committed; set them via Firebase Studio's
  # "Secrets" panel or export them in your shell before opening the workspace.
  env = {
    # ── Non-sensitive defaults ──────────────────────────────────────────────
    PORT                       = "8080";
    NODE_ENV                   = "development";
    TRYONYOU_DB_PATH           = "/tmp/tryonyou_leads.sqlite";
    LAFAYETTE_VERIFY_BASE_URL  = "https://tryonyou.lafayette.demo/verify/";
    JULES_MAIL_MAX_RESULTS     = "10";
    LINEAR_PAGE_SIZE           = "50";
    LINEAR_MAX_PAGES           = "10";
    GOOGLE_SHEETS_RANGE        = "Linear Tasks!A1";

    # ── Secrets — set these in Firebase Studio → Project Settings → Secrets ─
    # (leave blank here; they are injected at runtime)
    STRIPE_ENDPOINT_SECRET      = "";
    JULES_CRON_TOKEN            = "";
    GMAIL_REFRESH_TOKEN         = "";
    GMAIL_CLIENT_ID             = "";
    GMAIL_CLIENT_SECRET         = "";
    GEMINI_API_KEY              = "";
    GOOGLE_SERVICE_ACCOUNT_JSON = "";
    SPREADSHEET_ID              = "";
    PENNYLANE_API_KEY           = "";
    VERCEL_TOKEN                = "";
    PAU_TTS_ENDPOINT            = "";
    PAU_TTS_FALLBACK_AUDIO_URL  = "";
    LINEAR_API_KEY              = "";
    LINEAR_PROJECT_ID           = "";
    LINEAR_TEAM_ID              = "";
    LINEAR_API_TOKEN            = "";
    GOOGLE_SHEETS_ID            = "";
    GOOGLE_SHEETS_ACCESS_TOKEN  = "";

    # ── Frontend (Vite build-time) ──────────────────────────────────────────
    VITE_OAUTH_PORTAL_URL        = "";
    VITE_APP_ID                  = "";
    VITE_FRONTEND_FORGE_API_KEY  = "";
    VITE_FRONTEND_FORGE_API_URL  = "";
    VITE_ANALYTICS_ENDPOINT      = "";
    VITE_ANALYTICS_WEBSITE_ID    = "";

    # ── Optional overrides ──────────────────────────────────────────────────
    MAX_ENVIOS_DIARIOS   = "";
    JULES_AUDIT_LOG_PATH = "";
    LINEAR_SYNC_CRON_MS  = "";
  };

  idx = {
    extensions = [
      "ms-python.python"
      "ms-python.vscode-pylance"
      "esbenp.prettier-vscode"
      "dbaeumer.vscode-eslint"
    ];

    workspace = {
      onCreate = {
        install-python-deps = {
          command = "pip install -r api/requirements.txt";
          openFiles = [ "README.md" ];
        };
        install-node-deps = {
          command = "corepack enable && corepack pnpm install";
        };
      };

      onStart = {
        run-api = {
          command = "python api/index.py";
        };
        run-frontend = {
          command = "corepack pnpm run dev";
        };
      };
    };

    previews = {
      enable = true;
      previews = {
        web = {
          command = [ "corepack" "pnpm" "run" "dev" "--" "--port" "$PORT" "--host" "0.0.0.0" ];
          manager = "web";
          env = {
            PORT = "$PORT";
          };
        };
      };
    };
  };
}
