from pydantic import BaseModel

class ResponseModel(BaseModel):
    """Ответ API на статус уведомления"""
    success: bool = True
    message: str = ""
    data: dict | None = None

