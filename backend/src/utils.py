import json
from datetime import datetime
import os

frontend_domain = os.getenv("FRONTEND_DOMAIN")

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def response(status_code: int, body: dict, event: dict | None = None):
   
    base_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*",
    }
    

    return {
        "statusCode": status_code,
        "headers": base_headers,
        "body": json.dumps(body, cls=CustomJSONEncoder),
    }


def parse_json_body(event: dict) -> dict:
    if "body" not in event or event["body"] is None:
        return {}

    body = event["body"]
    if isinstance(body, str):
        return json.loads(body)

    return body