from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.auth import UserCreate, UserLogin, UserResponse, UserUpdate, Token
from ..services.auth_service import (
    authenticate_user,
    create_user,
    create_access_token,
    get_user_by_username,
    get_user_by_email,
    get_user_count,
    get_current_user,
    verify_password,
    get_password_hash
)
from ..models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists (if provided)
    if user_data.email and get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = create_user(
        db=db,
        username=user_data.username,
        password=user_data.password,
        email=user_data.email
    )

    return user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user_id=user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    # Check if trying to change password
    if user_data.new_password:
        if not user_data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to change password"
            )

        if not verify_password(user_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        current_user.hashed_password = get_password_hash(user_data.new_password)

    # Update email if provided
    if user_data.email is not None:
        # Check if email is taken by another user
        existing = get_user_by_email(db, user_data.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_data.email

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/status")
async def auth_status(db: Session = Depends(get_db)):
    """
    Check authentication status.
    Returns whether any users exist (for first-run setup).
    """
    user_count = get_user_count(db)
    return {
        "has_users": user_count > 0,
        "user_count": user_count
    }
