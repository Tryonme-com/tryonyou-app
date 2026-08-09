import os
from unittest.mock import patch
from api.financial_guard import _cors_preflight_no_content, _cors_json_response


def test_cors_preflight_origin_from_env():
    test_origin = "https://safe-domain.com"
    with patch.dict(os.environ, {"E50_CORS_ALLOW_ORIGIN": test_origin}):
        response = _cors_preflight_no_content()
        assert response.headers["Access-Control-Allow-Origin"] == test_origin


def test_cors_preflight_origin_fallback():
    if "E50_CORS_ALLOW_ORIGIN" in os.environ:
        del os.environ["E50_CORS_ALLOW_ORIGIN"]
    response = _cors_preflight_no_content()
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_cors_json_response_origin_from_env():
    test_origin = "https://safe-domain.com"
    with patch.dict(os.environ, {"E50_CORS_ALLOW_ORIGIN": test_origin}):
        response = _cors_json_response({"status": "ok"}, 200)
        assert response.headers["Access-Control-Allow-Origin"] == test_origin


def test_cors_json_response_origin_fallback():
    if "E50_CORS_ALLOW_ORIGIN" in os.environ:
        del os.environ["E50_CORS_ALLOW_ORIGIN"]
    response = _cors_json_response({"status": "ok"}, 200)
    assert response.headers["Access-Control-Allow-Origin"] == "*"
