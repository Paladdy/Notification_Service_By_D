from typing import AsyncGenerator
import pytest
from httpx import AsyncClient
from app.utils.redis_client import redis

pytestmark = pytest.mark.asyncio

async def test_create_notification(async_client: AsyncClient, auth_headers):
    data = {
        "type": "like",
        "text": "Someone liked your post!"
    }
    response = await async_client.post(
        "/notifications/",
        json=data,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    json_data = response.json()
    assert "data" in json_data
    notification = json_data["data"]
    assert notification["type"] == data["type"]
    assert notification["text"] == data["text"]
    assert "id" in notification
    assert "created_at" in notification

async def test_get_notifications_empty(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/notifications/", headers=auth_headers)
    assert response.status_code == 200
    
    json_data = response.json()
    assert "data" in json_data
    assert "items" in json_data["data"]
    assert len(json_data["data"]["items"]) == 0

async def test_get_notifications_with_data(async_client: AsyncClient, auth_headers):
    await redis.flushdb()

    notifications = [
        {"type": "like", "text": "First notification"},
        {"type": "comment", "text": "Second notification"}
    ]


    created_notifications = []
    for notif in notifications:
        response = await async_client.post("/notifications/", json=notif, headers=auth_headers)
        assert response.status_code == 200
        created_notifications.append(response.json()["data"])


    response = await async_client.get("/notifications/", headers=auth_headers)
    assert response.status_code == 200

    json_data = response.json()
    items = json_data["data"]["items"]
    

    assert len(items) == 2
    

    assert items[0]["text"] == "Second notification"
    assert items[1]["text"] == "First notification"
    

    for item in items:
        assert "id" in item
        assert "type" in item
        assert "created_at" in item

async def test_delete_notification(async_client: AsyncClient, auth_headers):
    create_data = {
        "type": "like",
        "text": "Notification to delete"
    }
    create_response = await async_client.post(
        "/notifications/",
        json=create_data,
        headers=auth_headers
    )
    assert create_response.status_code == 200
    
    notification_id = create_response.json()["data"]["id"]
    

    delete_response = await async_client.delete(
        f"/notifications/{notification_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 200
    

    list_response = await async_client.get("/notifications/", headers=auth_headers)
    assert list_response.status_code == 200
    items = list_response.json()["data"]["items"]
    assert len(items) == 0

async def test_delete_nonexistent_notification(async_client: AsyncClient, auth_headers):
    response = await async_client.delete(
        "/notifications/999999",
        headers=auth_headers
    )
    assert response.status_code == 404 