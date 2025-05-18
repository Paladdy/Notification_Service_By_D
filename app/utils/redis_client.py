from redis.asyncio import Redis
from app.config import settings


redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

