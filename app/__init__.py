from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import users_router, auth_router, decrypto_router

app = FastAPI()

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    users_router,
    prefix="/users",
    tags=["users"]
)

app.include_router(
    decrypto_router,
    prefix="/decrypto",
    tags=["decrypto"]
)
