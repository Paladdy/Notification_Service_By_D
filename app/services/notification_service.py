from app.models.notification import Notification
from app.models.user import User
from app.schemas.base import ResponseModel
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.utils.redis_client import redis
import json
import logging
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

logger = logging.getLogger(__name__)

# FIXME: Возможно стоит увеличить время кэша до 5 минут?
# Сейчас слишком часто ходим в базу при интенсивном использовании
NOTIFICATIONS_CACHE_TTL = 60  # 1 минута

# TODO: В будущем добавить:
# - Групповые уведомления
# - Поддержку вложений (картинки, файлы)
# - Websocket для real-time уведомлений
# - Фильтрацию по типу уведомлений

async def create_notification(notification_data: NotificationCreate, user_id: int) -> NotificationResponse:
    # Проверяем существование пользователя перед созданием уведомления
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=ResponseModel(success=False, message="Пользователь не найден", data=None).model_dump()
        )

    # Создаем новое уведомление в базе данных
    notification = await Notification.create(
        user=user,
        **notification_data.model_dump()
    )

    # Инвалидируем кэш уведомлений пользователя, так как появилось новое
    await redis.delete(f"notifications:{user_id}")
    # Подгружаем связанные данные пользователя
    await notification.fetch_related("user")

    return NotificationResponse.model_validate(notification)


async def get_notifications(limit: int, offset: int, user_id: int):
    # HACK: Пока используем простой ключ кэша, но возможно стоит добавить
    # хэширование параметров для более надежного кэширования
    cache_key = f"notifications:{user_id}:{limit}:{offset}"

    # Пытаемся получить данные из кэша
    cached = await redis.get(cache_key)
    if cached:
        # Если данные есть в кэше, возвращаем их
        return json.loads(cached)

    # TODO: Добавить сортировку по важности уведомлений
    # Если в кэше нет, получаем из базы данных с пагинацией
    # и сортировкой по дате создания (сначала новые)
    notifications = await Notification.filter(user_id=user_id).order_by('-created_at').offset(offset).limit(limit).all()
    
    logger.info(f'Найдены {len(notifications)} уведомления для user {user_id}')
    
    # Сериализуем уведомления для кэширования
    serialized = []
    for notification in notifications:
        notification_dict = {
            "id": notification.id,
            "type": notification.type,
            "text": notification.text,
            "created_at": notification.created_at.isoformat() if notification.created_at else None
        }
        serialized.append(notification_dict)
    
    logger.info(f'Serialized notifications: {serialized}')

    # FIXME: Возможно стоит добавить bulk операции для оптимизации?
    # Если есть данные, сохраняем их в кэш
    if serialized:
        await redis.setex(cache_key, NOTIFICATIONS_CACHE_TTL, json.dumps(serialized))

    return serialized

async def delete_notification(notification_id: int, user_id: int):
    # Ищем уведомление по ID и пользователю
    notification = await Notification.get_or_none(id=notification_id, user_id=user_id)

    if not notification:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено или доступ запрещён"
        )

    # TODO: Возможно стоит добавить soft delete?
    # Сейчас уведомления удаляются безвозвратно
    await notification.delete()

    # Чистим кэш уведомлений пользователя
    await redis.delete(f"notifications:{user_id}")

    return {
        "success": True,
        "message": "Уведомление удалено",
        "data": None
    }