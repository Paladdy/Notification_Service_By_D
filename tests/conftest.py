import pytest
import pytest_asyncio
from tortoise import Tortoise
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app
import asyncio
from app.utils.jwt_utils import create_jwt_token
from app.utils.redis_client import redis
from app.models.user import User
import bcrypt
import uuid



# Лайт для тестов
TEST_DB_URL = "sqlite://:memory:"

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_tests():
    await Tortoise.init(
        db_url=TEST_DB_URL,  # Лайт для тестов
        modules={"models": ["app.models.user", "app.models.notification"]}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

@pytest_asyncio.fixture(autouse=True)
async def cleanup_database(initialize_tests):
    """Cleanup для чистого состояние базы после тестов"""
    try:
        """Очищаем до тестов"""
        await redis.flushdb()
        conn = Tortoise.get_connection("default")
        await conn.execute_query("DELETE FROM notifications")
        await conn.execute_query("DELETE FROM users")
    except Exception as e:
        print(f"Ошибка во время cleanup: {e}")
    
    yield
    
    try:
        await redis.flushdb()
        conn = Tortoise.get_connection("default")
        await conn.execute_query("DELETE FROM notifications")
        await conn.execute_query("DELETE FROM users")
    except Exception as e:
        print(f"Ошибка во время cleanup: {e}")

@pytest_asyncio.fixture
async def test_user():
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpassword"
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = await User.create(
        username=unique_username,
        password_hash=password_hash
    )
    return user

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    base_url = "http://test"
    
    async with AsyncClient(transport=transport, base_url=base_url) as client:
        yield client

@pytest.fixture
def auth_headers(test_user):
    token = create_jwt_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture(scope="session")
def test_app():
    from app.main import app
    return app

@pytest.fixture(scope="session")
async def test_client(test_app):
    async with AsyncClient(base_url="http://test", transport=test_app) as client:
        yield client