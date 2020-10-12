from typing import Dict, Callable, Any, List, Optional
from enum import Enum

from ...users.database import User
from ..player_manager import PlayerManager
from .actions import Action, dict_to_action


class GameEvents(Enum):
    OnJoin = 1
    OnLeave = 2
    OnDisconnect = 3
    OnReconnect = 4


class Game:
    def __init__(self,
                 host: User,
                 send_action: Callable[[Action, Optional[List[str]]], None],
                 events: Dict[GameEvents, Callable[[PlayerManager], None]] = None,
                 ):
        if events is None:
            events = {}

        self._events: Dict[GameEvents, Callable[[PlayerManager], None]] = events
        self._send_action = send_action
        self._host = host

    def get_host(self) -> User:
        return self._host

    def execute_event(self, event: GameEvents, player: PlayerManager):
        if event in self._events:
            self._events[event](player)

    def execute_action(self, player: PlayerManager, action: Dict[str, Any]):
        self.reducer(player, dict_to_action(action))

    def reducer(self, player: PlayerManager, action: Action):
        pass
