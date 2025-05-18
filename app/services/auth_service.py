from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.utils.jwt_utils import create_jwt_token, decode_jwt_token
from app.config import settings
from datetime import timedelta
import bcrypt

async def register_user(register_data: RegisterRequest) -> TokenResponse:
    """Регистрация пользователя"""
    existing_user = await User.get_or_none(username=register_data.username)
    if existing_user:
        raise ValueError("Пользователь уже существует")

    # Хэшируем пароль перед сохранением
    hashed_password = bcrypt.hashpw(register_data.password.encode(), bcrypt.gensalt()).decode()

    # Создаем нового пользователя с хэшированным паролем
    user = await User.create(
        username=register_data.username,
        password_hash=hashed_password  # <-- важно: поле называется password_hash
    )

    # Генерируем токены
    access_token = create_jwt_token({"sub": str(user.id)})
    refresh_token = create_jwt_token(
        {"sub": str(user.id)},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id
    )


async def login_user(login_data: dict) -> TokenResponse:
    """Логин пользователя"""
    username = login_data["username"]
    plain_password = login_data["password"]

    # Ищем пользователя по username
    user = await User.get_or_none(username=username)
    if not user or not bcrypt.checkpw(plain_password.encode(), user.password_hash.encode()):
        raise ValueError("Неверные учетные данные")

    # Генерируем токены
    access_token = create_jwt_token({"sub": str(user.id)})
    refresh_token = create_jwt_token(
        {"sub": str(user.id)},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id
    )

async def refresh_user(refresh_data: dict) -> TokenResponse:
    """Обновление access токена через refresh токен"""
    refresh_token = refresh_data.get("refresh_token")
    if not refresh_token:
        raise ValueError("Refresh token не предоставлен")

    # Декодируем refresh токен
    payload = decode_jwt_token(refresh_token)

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Не удалось извлечь ID пользователя из refresh токена")

    # Проверяем, существует ли пользователь
    user = await User.get_or_none(id=int(user_id))
    if not user:
        raise ValueError("Пользователь не найден")

    # Генерируем новый access токен
    new_access_token = create_jwt_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_token,  # можно вернуть тот же refresh токен или создать новый
        user_id=int(user_id)
    )