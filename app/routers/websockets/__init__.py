from fastapi import APIRouter, WebSocket, Depends
from fastapi.responses import HTMLResponse
from enum import Enum, auto
from typing import Dict, Callable, List
import json

from ..users import User

"""
class Events(Enum):
    OnClientConnect = auto()
    OnClientDisconnect = auto()
    OnDataGet = auto()


class ConnectionManager():
    def __init__(self, 
        onClientConnect: Callable[[User], None], 
        onClientDisconnect: Callable[[User], None],
        onDataGet: Callable[[any], None]):

        self._onClientConnect = onClientConnect
        self._onClientDisconnect = onClientDisconnect
        self._onDataGet = onDataGet

        self.active_connections: Dict[str, WebSocket] = []

    async def connect(self, user: User, websocket: WebSocket):
        await websocket.accept()

        self.active_connections[user.id] = (websocket)
        self._onClientConnect(user)
        print(f"User {user.id} connected")

    def disconnect(self, user: User, websocket: WebSocket):
        self.active_connections.pop(user.id)
        self._onClientDisconnect(user)
        print(f"User {user.id} disconnected")

    async def send_to(self, message, user_id: str):
        await self.active_connections[user_id].send_json(json.dumps(message))

    async def send_group(self, message, user_ids: List[str]):
        for user_id in user_ids:
            await self.send_to(message, user_id)

    async def send_all(self, message):
        for user_id in self.active_connections.keys():
            await self.send_to(message, user_id)
            
    def get_data(self, message, user: User):
        self._onDataGet(message)
        print(f"Got message from {user.id}: {message}")


class Networker():
    def __init__(self, manager: ConnectionManager):
        self._manager = manager
        self._websocket_router = APIRouter()

        @self._websocket_router.websocket("/connect")
        async def websocket_endpoint(websocket: WebSocket, user: User = Depends(get_current_active_user)):
            await manager.connect(user, websocket)

            try:
                while True:
                    data = await websocket.receive_json()
                    manager.get_data(json.loads(data))
            except WebSocketDisconnect:
                manager.disconnect(user, websocket)

    def get_router(self) -> APIRouter:
        return self._websocket_router

"""