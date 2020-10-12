from fastapi import WebSocket
from uuid import UUID

from ..users.database import User
from .games.actions import action_to_json, Action


class PlayerManager:
    def __init__(self, user: User, websocket: WebSocket):
        self._user = user
        self._active = False
        self._websocket = websocket

    def get_user(self) -> User:
        return self._user

    def get_name(self) -> str:
        return self._user.username

    def get_uuid(self) -> UUID:
        return self._user.uuid

    def is_active(self) -> bool:
        return self._active

    def set_active(self, active: bool):
        self._active = active

    def send_action(self, action: Action):
        if not (self._websocket is None):
            self._websocket.send_json(action_to_json(action))
        else:
            print(f"{self.get_name()}'s websocket is None")

    def get_websocket(self) -> WebSocket:
        return self._websocket

    def disconnect(self):
        self._active = False
        if not (self._websocket is None):
            self._websocket.close()

    def reconnect(self, websocket: WebSocket):
        self._active = True
        self._websocket = websocket
