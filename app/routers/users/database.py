from fastapi import HTTPException, status
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
import os
import uuid

from .utils import get_password_hash

class UserFields(BaseModel):
    email: str
    username: str
    name: str
    lastname: str


class User(UserFields):
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserFields):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str]
    name: Optional[str]
    lastname: Optional[str]


class UserDB(User):
    id: uuid.UUID
    hashed_password: str

class UserShort(BaseModel):
    username: str
    name: str
    lastname: str

DATABASE_URL = os.getenv("DATABASE_URL")

client = MongoClient(DATABASE_URL)

db = client["platform"]

users_db = db["users"]

users_db.create_index("username", unique=True)
users_db.create_index("email", unique=True)

def add_user(user: UserCreate):
    if users_db.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken"
        )

    if users_db.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already taken"
        )

    userDB = UserDB(
        **dict(user),
        hashed_password=get_password_hash(user.password),
        id=uuid.uuid1()
    )
    
    users_db.insert_one(dict(userDB))

    return get_user(userDB.username)


def get_user(username: str):
    user = users_db.find_one({"username": username})
    return UserDB(**user)

def get_users():
    #users = users_db.find({"is_active": True})
    users = users_db.find()
    return [UserDB(**user) for user in users]
