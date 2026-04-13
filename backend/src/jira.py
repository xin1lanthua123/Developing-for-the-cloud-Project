import os
import boto3
import requests
from requests.auth import HTTPBasicAuth

# Global cache để tránh gọi SSM nhiều lần
_cached_jira_config = None

# SSM parameter names
SSM_PARAMS = {
    "base_url": "/incident-app/jira/base_url",
    "email": "/incident-app/jira/email",
    "token": "/incident-app/jira/token",
    "project_key": "/incident-app/jira/project_key",
}

# SSM client
ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))


def load_jira_config():
    """Load Jira config from SSM (cached)."""
    global _cached_jira_config
    if _cached_jira_config:
        return _cached_jira_config

    # Lấy tất cả các parameter cùng lúc
    resp = ssm.get_parameters(
        Names=list(SSM_PARAMS.values()),
        WithDecryption=True
    )

    param_map = {p["Name"]: p["Value"] for p in resp.get("Parameters", [])}

    # Kiểm tra missing
    missing = [name for name in SSM_PARAMS.values() if name not in param_map]
    if missing:
        raise RuntimeError(f"Missing Jira SSM parameters: {missing}")

    _cached_jira_config = {
        "base_url": param_map[SSM_PARAMS["base_url"]].rstrip("/"),
        "email": param_map[SSM_PARAMS["email"]],
        "token": param_map[SSM_PARAMS["token"]],
        "project_key": param_map[SSM_PARAMS["project_key"]],
    }

    return _cached_jira_config


def create_issue(summary: str, description: str, priority: str) -> str:
    """Tạo Jira issue và trả về issue key."""
    cfg = load_jira_config()

    url = f"{cfg['base_url']}/rest/api/3/issue"
    auth = HTTPBasicAuth(cfg["email"], cfg["token"])

    payload = {
        "fields": {
            "project": {"key": cfg["project_key"]},
            "summary": summary,
            "issuetype": {"name": "Task"},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                ],
            },
        }
    }

    r = requests.post(url, json=payload, auth=auth, headers={"Accept": "application/json"})
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Jira create issue failed: {r.status_code} {r.text}")

    data = r.json()
    return data["key"]


def add_comment(issue_key: str, comment_text: str):
    """Thêm comment vào Jira issue."""
    cfg = load_jira_config()

    url = f"{cfg['base_url']}/rest/api/3/issue/{issue_key}/comment"
    auth = HTTPBasicAuth(cfg["email"], cfg["token"])

    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": comment_text}]}
            ],
        }
    }

    r = requests.post(url, json=payload, auth=auth, headers={"Accept": "application/json"})
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Jira add comment failed: {r.status_code} {r.text}")