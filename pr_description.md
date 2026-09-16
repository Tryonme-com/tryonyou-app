🎯 **What:** The vulnerability fixed
The CORS middleware in `api/index.py` was configured with `allow_origins=["*"]`. This is an overly permissive CORS policy that allows any domain to read the responses of the API, regardless of whether they should have access.

⚠️ **Risk:** The potential impact if left unfixed
An attacker could host a malicious website and trick a user into visiting it. The malicious website could then make authenticated requests to the API on behalf of the user, potentially exposing sensitive biometric data, sizing information, or making unauthorized actions (like checking out).

🛡️ **Solution:** How the fix addresses the vulnerability
The wildcard `["*"]` in the `allow_origins` array was replaced with an explicit list of trusted origins.
It supports a dynamic list provided by the `E50_CORS_ALLOW_ORIGIN` environment variable (which is already used by `blindar_api_pagos.py` in the project), and if that is not provided, it falls back to a restricted list of explicitly trusted domains (e.g. `tryonyou.app`, `abvetos.com`) and localhost ports used for development. Tests were updated and added to ensure proper origin validation.
