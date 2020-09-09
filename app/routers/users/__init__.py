from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List

from .utils import is_valid_email
from .database import User, UserCreate, UserShort, add_user, get_user, get_users
from .auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, Token, get_current_active_user, create_access_token, get_current_superuser

users_router = APIRouter()
auth_router = APIRouter()

@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/register", response_model=User)
async def register(user: UserCreate):
    if not is_valid_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is not correct"
        )

    return add_user(user)


@users_router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@users_router.get("/all", response_model=List[UserShort])
async def get_all_users(current_user: User = Depends(get_current_superuser)):
    return get_users()

@users_router.get("/{username}", response_model=User)
async def get_user_by_username(username: str, current_user: User = Depends(get_current_superuser)):
    return get_user(username)
        