from src.handler import lambda_handler


def test_health():
    event = {
        "rawPath": "/health",
        "requestContext": {"http": {"method": "GET"}},
    }
    res = lambda_handler(event, None)

    assert res["statusCode"] == 200
    assert "ok" in res["body"]


def test_unknown_route():
    event = {
        "rawPath": "/unknown",
        "requestContext": {"http": {"method": "GET"}},
    }
    res = lambda_handler(event, None)

    assert res["statusCode"] == 404