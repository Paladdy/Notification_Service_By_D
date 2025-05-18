from tortoise.models import Model
from tortoise import fields

class User(Model):
    from datetime import datetime
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=128)
    avatar_url = fields.CharField(max_length=500, default="https://example.com/default_avatar.jpg ")
    created_at = fields.DatetimeField(auto_now_add=True)

    notifications: fields.ReverseRelation["Notification"]

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }



