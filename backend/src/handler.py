from auth import verify_cognito_jwt
import os
import uuid
from datetime import datetime, timezone
import boto3

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

import jwt  # PyJWT

import db
import jira
from models import Incident, VALID_STATUSES


UPLOAD_BUCKET_NAME = os.getenv("UPLOAD_BUCKET_NAME")
FRONTEND_URL = os.getenv("ORIGIN")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")

# Cognito issuer example:
# https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx
COGNITO_ISSUER = os.getenv("COGNITO_ISSUER")

app = FastAPI()

origins = [FRONTEND_URL]
# CORS (cho frontend gọi API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # production thì đổi sang domain của bạn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------
# AUTH HELPERS
# -----------------------
def get_token_from_header(request: Request) -> str:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    return auth.replace("Bearer ", "").strip()




COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")


def get_user_id_from_jwt(token: str) -> str:
    payload = verify_cognito_jwt(token, audience=COGNITO_CLIENT_ID)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized (no user_id in token)")

    return user_id


def get_current_user_id(request: Request) -> str:
    token = get_token_from_header(request)
    return get_user_id_from_jwt(token)


# -----------------------
# ROUTES
# -----------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/incidents")
async def create_incident(request: Request):
    user_id = get_current_user_id(request)

    body = await request.json()
    title = body.get("title")
    description = body.get("description")
    priority = (body.get("priority") or "LOW").upper()

    incident = Incident.create(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
    )

    db.put_incident(incident.__dict__)

    try:
        issue_key = jira.create_issue(
            summary=f"[{incident.priority}] {incident.title}",
            description=incident.description,
            priority=incident.priority,
        )

        updated = db.set_jira_issue_key(
            incident_id=incident.incident_id,
            user_id=user_id,
            jira_issue_key=issue_key,
        )

        return {"message": "incident created", "incident": updated}

    except Exception as e:
        return {
            "message": "incident created (jira integration failed)",
            "incident": incident.__dict__,
            "jira_error": str(e),
        }


@app.get("/incidents")
def list_incidents(request: Request):
    user_id = get_current_user_id(request)

    items = db.list_incidents(user_id=user_id)
    return {"incidents": items}


@app.get("/incidents/{incident_id}")
def get_incident_detail(incident_id: str, request: Request):
    user_id = get_current_user_id(request)

    item = db.get_incident(incident_id=incident_id, user_id=user_id)
    if not item:
        raise HTTPException(status_code=404, detail="incident not found")

    item["comments"] = item.get("comments", [])
    item["attachments"] = item.get("attachments", [])

    return {"incident": item}


@app.patch("/incidents/{incident_id}")
async def update_incident(incident_id: str, request: Request):
    user_id = get_current_user_id(request)

    body = await request.json()
    new_status = body.get("status")

    if new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {VALID_STATUSES}")

    updated = db.update_incident_status(
        incident_id=incident_id,
        user_id=user_id,
        status=new_status
    )

    if not updated:
        raise HTTPException(status_code=404, detail="incident not found")

    issue_key = updated.get("jira_issue_key")
    if issue_key:
        try:
            jira.add_comment(issue_key, f"Incident status updated to: {new_status}")
        except Exception:
            pass

    return {"message": "incident updated", "incident": updated}


@app.post("/incidents/{incident_id}/comments")
async def add_comment(incident_id: str, request: Request):
    user_id = get_current_user_id(request)

    body = await request.json()
    text = body.get("comment") or body.get("text")

    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="comment is required")

    comment = {
        "comment_id": str(uuid.uuid4()),
        "text": text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    updated = db.add_comment(
        incident_id=incident_id,
        user_id=user_id,
        comment=comment
    )

    if not updated:
        raise HTTPException(status_code=404, detail="incident not found")

    issue_key = updated.get("jira_issue_key")
    if issue_key:
        try:
            jira.add_comment(issue_key, f"New comment: {text}")
        except Exception:
            pass

    return {"message": "comment added", "incident": updated}


@app.post("/incidents/{incident_id}/attachments/presign")
async def presign_upload(incident_id: str, request: Request):
    user_id = get_current_user_id(request)

    if not UPLOAD_BUCKET_NAME:
        raise HTTPException(status_code=500, detail="UPLOAD_BUCKET_NAME not configured")

    body = await request.json()

    item = db.get_incident(incident_id=incident_id, user_id=user_id)
    if not item:
        raise HTTPException(status_code=404, detail="Incident not found")

    file_name = body.get("filename", "file.bin")
    content_type = body.get("contentType") or body.get("content_type") or "application/octet-stream"

    safe_filename = file_name.replace("/", "_").replace("\\", "_")
    object_key = f"incidents/{incident_id}/{uuid.uuid4()}-{safe_filename}"

    s3 = boto3.client("s3")
    presigned_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": UPLOAD_BUCKET_NAME,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=300,
    )

    now = datetime.now(timezone.utc).isoformat()
    attachment = {
        "attachment_id": str(uuid.uuid4()),
        "file_name": safe_filename,
        "content_type": content_type,
        "uploaded_at": now,
        "object_key": object_key,
    }

    updated = db.add_attachment(
        incident_id=incident_id,
        user_id=user_id,
        attachment=attachment
    )

    return {
        "presigned_url": presigned_url,
        "object_key": object_key,
        "bucket": UPLOAD_BUCKET_NAME,
        "attachment": attachment,
        "incident": updated,
    }


@app.get("/incidents/{incident_id}/attachments/{attachment_id}/download")
def download_attachment(incident_id: str, attachment_id: str, request: Request):
    user_id = get_current_user_id(request)

    item = db.get_incident(incident_id=incident_id, user_id=user_id)
    if not item:
        raise HTTPException(status_code=404, detail="incident not found")

    attachments = item.get("attachments", [])
    att = next((a for a in attachments if a.get("attachment_id") == attachment_id), None)

    if not att:
        raise HTTPException(status_code=404, detail="attachment not found")

    s3 = boto3.client("s3")
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": UPLOAD_BUCKET_NAME,
            "Key": att["object_key"],
        },
        ExpiresIn=300,
    )

    return {"download_url": url}