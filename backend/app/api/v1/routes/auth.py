import structlog
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

from app.core.config import Settings, get_settings
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.models.auth import (
    AuthResponse,
    LoginRequest,
    MeResponse,
    RegisterRequest,
    UpdateProfileRequest,
)
from app.services.auth import (
    create_access_token,
    generate_api_key,
    hash_password,
    verify_password,
)

router = APIRouter()
logger = structlog.get_logger()


def _set_session_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key="clickit_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=not settings.debug,
        max_age=settings.jwt_expiry_minutes * 60,
        path="/",
    )


@router.post("/auth/register", response_model=AuthResponse, status_code=201)
async def register(
    request: RegisterRequest,
    response: Response,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Email already registered")

    api_key = generate_api_key()
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        tier="free",
        grandma_mode=False,
        language="en",
        api_key=api_key,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, user.email)
    _set_session_cookie(response, token, settings)

    logger.info("user_registered", user_id=user.id, email=user.email)

    return AuthResponse(
        user_id=user.id,
        email=user.email,
        tier=user.tier,
        grandma_mode=user.grandma_mode,
        api_key=api_key,
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    response: Response,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(user.id, user.email)
    _set_session_cookie(response, token, settings)

    logger.info("user_login", user_id=user.id)

    return AuthResponse(
        user_id=user.id,
        email=user.email,
        tier=user.tier,
        grandma_mode=user.grandma_mode,
    )


@router.post("/auth/logout")
async def logout(
    response: Response,
    _current_user: User = Depends(get_current_user),
):
    response.delete_cookie("clickit_session", path="/")
    return {"message": "Logged out"}


@router.get("/auth/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return MeResponse(
        user_id=current_user.id,
        email=current_user.email,
        tier=current_user.tier,
        grandma_mode=current_user.grandma_mode,
        language=current_user.language or "en",
        api_key=current_user.api_key,
    )


@router.patch("/auth/profile", response_model=MeResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if request.grandma_mode is not None:
        current_user.grandma_mode = request.grandma_mode
    if request.language is not None:
        current_user.language = request.language

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    logger.info("profile_updated", user_id=current_user.id)

    return MeResponse(
        user_id=current_user.id,
        email=current_user.email,
        tier=current_user.tier,
        grandma_mode=current_user.grandma_mode,
        language=current_user.language or "en",
        api_key=current_user.api_key,
    )


@router.post("/auth/rotate-api-key")
async def rotate_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_key = generate_api_key()
    current_user.api_key = new_key
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    logger.info("api_key_rotated", user_id=current_user.id)

    return {"api_key": new_key}
