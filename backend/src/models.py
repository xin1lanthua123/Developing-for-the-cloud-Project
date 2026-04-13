from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


VALID_STATUSES = {"OPEN", "IN_PROGRESS", "RESOLVED"}
VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH"}


@dataclass
class Incident:
    incident_id: str
    title: str
    user_id: str
    description: str
    priority: str
    status: str
    created_at: str
    updated_at: str
    jira_issue_key: str | None = None
    comments: list | None = None
    attachments: list | None = None

    @staticmethod
    def create(user_id: str, title: str, description: str, priority: str):
        if not user_id:
            raise ValueError("Userid are required")
        if not title or not isinstance(title, str):
            raise ValueError("title is required")

        if not description or not isinstance(description, str):
            raise ValueError("description is required")

        if priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}")

        now = datetime.now(timezone.utc).isoformat()
        return Incident(
            incident_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            status="OPEN",
            created_at=now,
            updated_at=now,
            comments=[],
            attachments=[]
        )
    
