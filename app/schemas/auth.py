from pydantic import BaseModel


class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""
    username: str
    password: str

class LoginRequest(BaseModel):
    """Запрос на авторизацию"""
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    """Для ответа с токенами"""
    access_token: str
    refresh_token: str
    user_id: int