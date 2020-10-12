from fastapi import APIRouter, Depends, WebSocket, HTTPException, status
from starlette.websockets import WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import json

from ..users.auth import get_current_active_user
from ..users.database import User

from .player_manager import PlayerManager
from .games_manager import GamePost, GameShortGet, GamesManager, GameStatus

games_manager = GamesManager()

games_router = APIRouter()


class CreateGameResponse(BaseModel):
    code: str


class StatusGet(BaseModel):
    status: GameStatus


@games_router.post("/", response_model=CreateGameResponse)
async def create_game(game: GamePost,
                      user: User = Depends(get_current_active_user)):
    return CreateGameResponse(
        code=games_manager.create_game(user, game)
    )


@games_router.get("/", response_model=List[GameShortGet])
async def get_public_games(_: User = Depends(get_current_active_user)):
    return games_manager.get_public_games()


@games_router.get("/{game_id}/status", response_model=StatusGet)
async def get_game_status(game_id: str,
                          _: User = Depends(get_current_active_user)
                          ):
    game = games_manager.find_game(game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

    return StatusGet(
        status=games_manager.find_game(game_id).get_status()
    )


@games_router.delete("/{game_id}")
async def delete_game(game_id: str,
                      user: User = Depends(get_current_active_user)
                      ):
    games_manager.delete_game(user, game_id)


@games_router.post("/{game_id}/add_to_game", response_model=StatusGet)
async def add_to_game(game_id: str,
                          user: User = Depends(get_current_active_user)
                          ):
    game = games_manager.find_game(game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

    if game.is_full():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Server is full"
        )

    game.add_player_to_queue(user)

    return StatusGet(
        status=game.get_status()
    )


@games_router.post("/{game_id}/connect")
async def connect_to_game_without_websocket(game_id: str,
                                    user: User = Depends(
                                        get_current_active_user)
                                    ):
    game = games_manager.find_game(game_id)

    if not game.can_join(user):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Error"
        )

    game.add_player(user)


@games_router.websocket("/{game_id}/ws")
async def connect_to_game(game_id: str,
                  websocket: WebSocket,
                  user: User = Depends(get_current_active_user)
                  ):
    await websocket.accept()

    game = games_manager.find_game(game_id)

    if not game.can_join(user):
        await websocket.close()
        return

    await websocket.send_text("Joining")
    player = game.add_player(user, websocket)
    if player is None:
        await websocket.close()
        return

    try:
        while True:
            action_json = await websocket.receive_json()
            action_dict = json.loads(action_json)
            game.receive_action(player, action_dict)
    except WebSocketDisconnect:
        game.disconnect(player)
