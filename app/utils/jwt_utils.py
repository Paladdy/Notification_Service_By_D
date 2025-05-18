import jwt
from fastapi import Depends, HTTPException, status
from typing import Optional
from datetime import datetime, timedelta
from app.config import settings
from app.utils.logger import logger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# TODO: В будущих версиях добавить:
# - Поддержку refresh token rotation
# - Blacklist для отозванных токенов
# - Поддержку разных типов токенов (access, refresh, temporary)
# - Возможность отзыва всех токенов пользователя

"""Cхема для зависимости для получения токена из заголовка"""
bearer_scheme = HTTPBearer(auto_error=False)


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создаем токен"""
    # Копируем данные, чтобы не изменять оригинальный словарь
    to_encode = data.copy()
    
    # FIXME: Возможно стоит добавить проверку на максимальное время жизни токена?
    # Сейчас теоретически можно создать токен с очень большим сроком
    
    # Устанавливаем время истечения токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Если время не указано, используем значение из настроек
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Добавляем время истечения в данные токена
    to_encode.update({"exp": expire})
    
    # HACK: Возможно стоит добавить в токен больше информации о пользователе,
    # чтобы меньше ходить в базу? Например, username и роли
    
    # Кодируем токен с использованием секретного ключа и алгоритма из настроек
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    logger.info(f"Token created for {data}")
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    """Декодируем JWT токен и проверяем подпись"""
    try:
        # TODO: Добавить проверку на валидность алгоритма
        # Сейчас принимаем любой алгоритм из настроек
        
        # Явно преобразуем к строке, если пришёл как bytes
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        # Декодируем токен и проверяем его подпись
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        # Если токен истёк
        logger.error("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.PyJWTError as e:
        # FIXME: Возможно стоит добавить более подробную обработку различных JWT ошибок?
        # Сейчас все ошибки валидации выглядят одинаково для клиента
        logger.error(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
    # TODO: Добавить кэширование информации о пользователе
    # Сейчас при каждом запросе проверяем токен
    
    # Проверяем наличие токена в заголовке
    if credentials is None or credentials.credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Декодируем и проверяем токен
        payload = decode_jwt_token(credentials.credentials)
        user_id = payload.get("sub")
        
        # HACK: Возможно стоит добавить проверку существования пользователя в базе?
        # Сейчас мы просто верим токену
        
        # Проверяем, что в токене есть ID пользователя и он числовой
        if not user_id or not user_id.isdigit():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильный токен"
            )
        return int(user_id)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный токен"
        )