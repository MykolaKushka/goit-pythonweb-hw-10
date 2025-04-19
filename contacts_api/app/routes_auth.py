from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Request, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.cloudinary_utils import upload_avatar

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token
from app.auth import hash_password, verify_password
from app.jwt_utils import (
    create_access_token,
    create_email_token,
    decode_email_token
)
from app.email_utils import send_verification_email
from app.dependencies import get_current_user

from slowapi.errors import RateLimitExceeded
from app.limiter_config import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_email_token(new_user.email)
    background_tasks.add_task(send_verification_email, new_user.email, token)

    return new_user


@router.post("/login", response_model=Token)
async def login_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email = decode_email_token(token)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    await db.commit()
    return {"message": "Email verified successfully!"}


@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def get_my_profile(
    request: Request, 
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user

@router.post("/avatar", response_model=UserResponse)
async def update_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    content = await file.read()
    url = upload_avatar(content, public_id=str(current_user.id))

    current_user.avatar_url = url
    await db.commit()
    await db.refresh(current_user)

    return current_user