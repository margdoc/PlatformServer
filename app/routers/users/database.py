from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
import os

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
    hashed_password: str


DATABASE_URL = os.getenv("DATABASE_URL")

client = MongoClient(DATABASE_URL)

db = client["platform"]

users_db = db["users"]

users_db.create_index("username", unique=True)
users_db.create_index("email", unique=True)

def add_user(user: UserCreate):
    userDB = UserDB(
        **dict(user), 
        hashed_password=get_password_hash(user.password)
    )
    users_db.insert_one(dict(userDB))

def get_user(username: str):
    user = users_db.find_one({"username": username})
    return UserDB(**user)