from fastapi import Depends, status, HTTPException, Request, WebSocket
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from .database import User, get_user
from ...utils import get_password_hash, verify_password

import os

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    accessToken: str
    tokenType: str


class TokenData(BaseModel):
    username: str


class AuthBearer(OAuth2PasswordBearer):
    async def __call__(self,
                       request: Request = None,
                       websocket: WebSocket = None
                       ) -> Optional[str]:
        request = request or websocket
        if not request:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authenticated"
                )
            return None
        return await super().__call__(request)


oauth2_scheme = AuthBearer(tokenUrl="auth/login")


def authenticate_user(username: str, password: str):
    user = get_user(username=username)
    if not user:
        return False
    elif not verify_password(password, user.hashedPassword):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    """
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)):
    if not current_user.isActive:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(
        current_user: User = Depends(get_current_active_user)):
    if not current_user.isSuperuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not superuser"
        )
    return current_user
