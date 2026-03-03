"""Auth router: /auth/register, /auth/login, /auth/me"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.auth import hash_password, verify_password, create_access_token, decode_token
from app.schemas.common import APIResponse
from app.services.gdrive_sync import mark_modified

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    display_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    model_config = {"from_attributes": True}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=APIResponse[TokenResponse], status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new account and return a JWT immediately."""
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "Username already taken."},
        )
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "message": "Email already registered."},
        )
    user = User(
        username=payload.username,
        email=payload.email,
        display_name=payload.display_name or payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    mark_modified()

    token = create_access_token(user.id, user.username)
    return APIResponse.ok(
        data=TokenResponse(
            access_token=token,
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
        ),
        message="Account created successfully!",
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with username + password, return JWT."""
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Invalid username or password."},
        )
    token = create_access_token(user.id, user.username)
    return APIResponse.ok(
        data=TokenResponse(
            access_token=token,
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
        ),
        message="Login successful!",
    )


@router.get("/me", response_model=APIResponse[UserOut])
def get_me(authorization: Optional[str] = None, db: Session = Depends(get_db)):
    """Return the current user decoded from their JWT Bearer token.

    Pass the token as:  Authorization: Bearer <token>
    """
    from fastapi import Request

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Missing or malformed Authorization header."},
        )
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Token is invalid or has expired."},
        )
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found."})
    return APIResponse.ok(data=UserOut.model_validate(user))

