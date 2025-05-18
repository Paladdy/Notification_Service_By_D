from typing import AsyncGenerator
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_register_success(async_client: AsyncClient):
    data = {
        "username": "newuser",
        "password": "password123"
    }
    response = await async_client.post(
        "/auth/register",
        json=data
    )
    assert response.status_code == 200
    
    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data
    assert "user_id" in json_data

async def test_register_duplicate_username(async_client: AsyncClient):
    data = {
        "username": "duplicate_user",
        "password": "password123"
    }
    response1 = await async_client.post(
        "/auth/register",
        json=data
    )
    assert response1.status_code == 200

    response2 = await async_client.post(
        "/auth/register",
        json=data
    )
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Пользователь уже существует"

async def test_login_success(async_client: AsyncClient):
    user_data = {
        "username": "loginuser",
        "password": "password123"
    }
    await async_client.post(
        "/auth/register",
        json=user_data
    )

    response = await async_client.post(
        "/auth/login",
        json=user_data
    )
    assert response.status_code == 200
    
    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data
    assert "user_id" in json_data

async def test_login_invalid_credentials(async_client: AsyncClient):
    data = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    response = await async_client.post(
        "/auth/login",
        json=data
    )
    assert response.status_code == 400
    assert "detail" in response.json() 