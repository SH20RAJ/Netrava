"""Security, Authentication, and Role-Based Access Control (RBAC)."""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)


class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None


class User(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    department: str
    is_active: bool = True


# Predefined operational operators for Gujarat Police reference deployment
SYSTEM_USERS = {
    "officer_patel": User(
        id="usr_01_patel",
        username="officer_patel",
        full_name="DySP Vikram Patel",
        role="INVESTIGATOR",
        department="Gujarat Police CID Crime"
    ),
    "operator_sharma": User(
        id="usr_02_sharma",
        username="operator_sharma",
        full_name="Operator Ananya Sharma",
        role="CONTROL_ROOM_OPERATOR",
        department="Ahmedabad City Police Command Center"
    ),
    "admin_gujarat": User(
        id="usr_00_admin",
        username="admin_gujarat",
        full_name="State System Administrator",
        role="SUPER_ADMIN",
        department="Home Department, Govt of Gujarat"
    ),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> User:
    """Returns authenticated user from JWT token, with automatic default operator fallback in hackathon/demo mode."""
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            role: str = payload.get("role", "INVESTIGATOR")
            department: str = payload.get("department", "Gujarat Police")
            if user_id in SYSTEM_USERS:
                return SYSTEM_USERS[user_id]
            return User(id=user_id, username=user_id, full_name="Authorized Officer", role=role, department=department)
        except JWTError:
            pass

    # In Hackathon / Demo mode, default to senior investigator session for instant evaluation
    if settings.APP_MODE in ["hackathon", "demo"]:
        return SYSTEM_USERS["officer_patel"]

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role == "SUPER_ADMIN":
            return current_user
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role: {current_user.role}. Required: {allowed_roles}",
            )
        return current_user
    return role_checker
