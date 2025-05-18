from tortoise import fields, Model
from enum import Enum


class NotificationType(str, Enum):
    # Ограничиваем только этими значениями с помощью enum
    like = 'like'
    comment = 'comment'
    repost = 'repost'

class Notification(Model):
    from datetime import datetime
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="notifications")
    type = fields.CharEnumField(NotificationType)
    text = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "text": self.text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user": self.user.to_dict() if self.user else None,

        }