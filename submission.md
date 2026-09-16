🎯 **What:**
Fixed an overly permissive CORS configuration in FastAPI's Core API (`api/index.py`). The application previously used `allow_origins=["*"]`, allowing any domain to execute requests across origin boundaries.

⚠️ **Risk:**
Using `*` for CORS origins is a major security vulnerability. It permits malicious websites to make cross-origin requests on behalf of a user who may already be authenticated or hold session data, bypassing the Same-Origin Policy and exposing private actions and biometric functionality.

🛡️ **Solution:**
Replaced `["*"]` with an environment-based approach. The application now loads allowed origins from the `E50_CORS_ALLOW_ORIGIN` environment variable. If the variable is not set, it fails securely by falling back to explicitly whitelisting `https://tryonyou.app` and `http://localhost:5173`. Added corresponding robust unit tests using `unittest` and `TestClient` to enforce strict domain validation and ensure regressions do not occur.
