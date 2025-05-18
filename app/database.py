from tortoise import Tortoise
from app.config import settings
import asyncio


TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models.user", "app.models.notification"],
            "default_connection": "default",
        }
    },
}

async def init_db():
    """Делаем ретраи чтобы не падало первое включение основной app"""
    retries = 0
    while True:
        try:
            await Tortoise.init(config=TORTOISE_ORM)
            print("База данных подключена")
            await Tortoise.generate_schemas()
            break
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            if retries > 5:
                raise
            retries += 1
            print(f"Ждём {retries} секунду(ы) перед повторной попыткой...")
            await asyncio.sleep(retries)