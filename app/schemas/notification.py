from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from app.models.notification import Notification as NotificationModel

class NotificationType(str, Enum):
    like = "like"
    comment = "comment"
    repost = "repost"


class UserSchema(BaseModel):
    id: int
    username: str
    avatar_url: str

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    type: NotificationType
    text: str


class NotificationResponse(BaseModel):
    id: int
    user: UserSchema
    type: NotificationType
    text: str
    created_at: datetime
    user_id: int

    @classmethod
    def model_validate(cls, obj: NotificationModel, *args, **kwargs):
        return cls(
            id=obj.id,
            user=obj.user,
            type=obj.type,
            text=obj.text,
            created_at=obj.created_at,
            user_id=obj.user.id # Поскольку юзаем foreign key
        )

    class Config:
        from_attributes = True