import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime,timezone
import uuid
DDB_TABLE_NAME = os.getenv("DDB_TABLE_NAME", "incidents")


def get_table():
    region = os.getenv("AWS_REGION", "us-east-1")
    dynamodb = boto3.resource("dynamodb",region_name=region)
    return dynamodb.Table(DDB_TABLE_NAME)


def put_incident(item: dict):
    table = get_table()
    table.put_item(Item=item)


def get_incident(incident_id: str,user_id: str) -> dict | None:
    table = get_table()
    resp = table.get_item(Key={"incident_id": incident_id})
    item = resp.get("Item")
    if not item:
        return None
    if item.get("user_id") != user_id:
        return None
    item["comments"] = item.get("comments", [])
    item["attachments"] = item.get("attachments", [])

    return item


def list_incidents(user_id: str, limit: int = 50) -> list[dict]:
    table = get_table()

    resp = table.query(
        IndexName="user_id-created_at-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        Limit=limit,
        ScanIndexForward=False
    )

    items = resp.get("Items", [])

    for i in items:
        i["comments"] = i.get("comments", [])
        i["attachments"] = i.get("attachments", [])

    return items


def update_incident_status(incident_id: str,user_id: str,status: str) -> dict:

    item = get_incident(incident_id, user_id)
    if not item:
        raise ValueError("incident not found or forbidden")
    
    table = get_table()

    try:
        resp = table.update_item(
            Key={"incident_id": incident_id},
            UpdateExpression="SET #s = :s, updated_at = :u",
            ConditionExpression="user_id = :uid",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": status,
                ":u": __import__("datetime").datetime.utcnow().isoformat(),
                ":uid" : user_id,
            },
            ReturnValues="ALL_NEW",
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return None
    
    updated = resp["Attributes"]
    updated["comments"] = updated.get("comments", [])
    updated["attachments"] = updated.get("attachments", [])

    return updated

def set_jira_issue_key(incident_id: str,user_id: str, jira_issue_key: str) -> dict:
    table = get_table()
    now = datetime.now(timezone.utc).isoformat()

    try:
        resp = table.update_item(
            Key={"incident_id": incident_id},
            UpdateExpression="SET jira_issue_key = :k, updated_at = :u",
            ConditionExpression="user_id = :uid",
            ExpressionAttributeValues={
                ":k": jira_issue_key,
                ":u": now,
                ":uid" : user_id,
            },
            ReturnValues="ALL_NEW",
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return None
    
    updated = resp["Attributes"]
    updated["comments"] = updated.get("comments", [])
    updated["attachments"] = updated.get("attachments", [])

    return updated

def add_comment(incident_id: str,user_id: str, comment: dict) -> dict:
    item = get_incident(incident_id, user_id)
    if not item:
        raise ValueError("incident not found or forbidden")
    table = get_table()

    now = __import__("datetime").datetime.utcnow().isoformat()

    try:
        resp = table.update_item(
            Key={"incident_id": incident_id},
            UpdateExpression="SET comments = list_append(if_not_exists(comments, :empty), :c), updated_at = :u",
            ConditionExpression="user_id = :uid",
            ExpressionAttributeValues={
                ":c": [comment],
                ":empty": [],
                ":u": now,
                ":uid" : user_id,
            },
            ReturnValues="ALL_NEW",
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return None
    
    updated = resp["Attributes"]
    updated["comments"] = updated.get("comments", [])
    updated["attachments"] = updated.get("attachments", [])

    return updated


def add_attachment(incident_id: str,user_id: str, attachment: dict) -> dict:
    item = get_incident(incident_id, user_id)
    if not item:
        raise ValueError("incident not found or forbidden")
    table = get_table()
    now = datetime.now(timezone.utc).isoformat()

    try:
        resp = table.update_item(
            Key={"incident_id": incident_id},
            UpdateExpression="""
                SET attachments = list_append(if_not_exists(attachments, :empty), :a),
                    updated_at = :u
            """,
            ConditionExpression="user_id = :uid",
            ExpressionAttributeValues={
                ":a": [attachment],
                ":empty": [],
                ":u": now,
                ":uid" : user_id,
            },
            ReturnValues="ALL_NEW",
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return None
    
    updated = resp["Attributes"]
    updated["comments"] = updated.get("comments", [])
    updated["attachments"] = updated.get("attachments", [])

    return updated