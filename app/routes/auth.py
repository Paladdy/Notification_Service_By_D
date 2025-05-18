from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.services.auth_service import register_user, login_user, refresh_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
async def register(register_data: RegisterRequest):
    try:
        return await register_user(register_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    try:
        return await login_user(login_data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_data: RefreshRequest):
    try:
        return await refresh_user(refresh_data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))