from src.handler import lambda_handler

event = {
    "rawPath": "/health",
    "requestContext": {"http": {"method": "GET"}},
}

print(lambda_handler(event, None))