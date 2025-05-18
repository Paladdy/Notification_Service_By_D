from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.notification import NotificationCreate
from app.services.notification_service import create_notification, get_notifications, delete_notification
from app.utils.jwt_utils import get_current_user
from app.schemas.base import ResponseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


#----Создаем уведомление
@router.post("/", response_model=ResponseModel)
async def create_notif(notification_data: NotificationCreate, user_id: int = Depends(get_current_user)):
    logger.info(f"Создаем уведомление с: {notification_data}, user_id: {user_id}")
    result = await create_notification(notification_data, user_id)
    logger.info(f"Уведомление создано: {result}")
    return ResponseModel(
        success=True,
        message="Уведомление успешно создано",
        data=result.model_dump()
    )

#----Получить список уведомлений
@router.get("/", response_model=ResponseModel)
async def list_notifs(
        limit: int = 10,
        offset: int = 0,
        user_id: int = Depends(get_current_user)
):
    logger.info(f"Getting notifications for user_id: {user_id}, limit: {limit}, offset: {offset}")
    result = await get_notifications(limit, offset, user_id)
    logger.info(f"Найдены {len(result)} уведомления")
    return ResponseModel(
        success=True,
        message="Список уведомлений",
        data={"items": result, "total": len(result)}
    )

#----Удалить уведомление
@router.delete("/{notif_id}", response_model=ResponseModel)
async def delete_notif(notif_id: int, user_id: int = Depends(get_current_user)):
    logger.info(f"Удаление уведомления {notif_id} для user_id: {user_id}")
    await delete_notification(notif_id, user_id)
    logger.info(f"Удаленное уведомление {notif_id}")
    return ResponseModel(success=True, message="Уведомление удалено")