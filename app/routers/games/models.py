from fastapi_utils.enums import StrEnum

from pydantic import BaseModel
from typing import Optional
from enum import auto


# List of all games
class GameStatus(StrEnum):
    Lobby = auto()
    NeuroshimaHex = auto()


class GamePost(BaseModel):
    name: str
    password: Optional[str]
    private: bool
    description: Optional[str]
    maxPlayers: int
    hotJoin: bool


class GameShortGet(BaseModel):
    name: str
    hasPassword: bool
    description: Optional[str]
    players: int
    maxPlayers: int
    status: GameStatus
    hotJoin: bool
    private: bool


class GameGet(GameShortGet):
    id: str
