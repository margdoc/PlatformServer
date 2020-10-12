from fastapi import WebSocket
from typing import Dict, List, Optional, Any, Set
from uuid import UUID

from ..users.database import User
from .player_manager import PlayerManager
from .models import GamePost, GameGet, GameStatus, GameShortGet
from .games.game import GameEvents, Game
from .games.lobby import Lobby
from .games.actions import Action


class GameManager:
    def __init__(self, host: User, game: GamePost, _id: str):
        self._host = host
        self._players: Dict[UUID, PlayerManager] = {}
        self._settings = game
        self._status: GameStatus = GameStatus.Lobby
        self._id = _id
        self._game: Game = Lobby(host, self.send_action)
        self._waiting_queue: Set[UUID] = set()

    def send_action(self, action: Action, players: Optional[List[UUID]] = None):
        players_to_send = self.get_players() if players is None else \
            list(map(self.get_player, players))

        for player in players_to_send:
            player.send_action(action)

    def is_in_game(self, uuid: UUID):
        return uuid in self._players

    def disconnect(self, player: PlayerManager):
        self._game.execute_event(GameEvents.OnDisconnect, player)
        player.disconnect()

    def add_player_to_queue(self, user: User):
        self._waiting_queue.add(user.uuid)

    def can_join(self, user: User) -> bool:
        return user.uuid in self._waiting_queue

    def add_player(self, user: User, websocket: WebSocket = None) \
            -> Optional[PlayerManager]:

        if not (user.uuid in self._waiting_queue):
            return None

        self._waiting_queue.remove(user.uuid)

        if self.is_in_game(user.uuid):
            player = self.get_player(user.uuid)
            self._game.execute_event(GameEvents.OnReconnect, player)
        else:
            player = PlayerManager(user, websocket)
            self._players[user.uuid] = player
            self._game.execute_event(GameEvents.OnJoin, player)

        return player

    def remove_player(self, player: PlayerManager):
        self._game.execute_event(GameEvents.OnLeave, player)
        del self._players[player.get_uuid()]

    def get_player(self, uuid: UUID) -> Optional[PlayerManager]:
        if self.is_in_game(uuid):
            return None
        return self._players[uuid]

    def get_players(self) -> List[PlayerManager]:
        return list(self._players.values())

    def get_players_count(self) -> int:
        return len(self._players)

    def get_status(self) -> GameStatus:
        return self._status

    def get_game_info(self) -> GameGet:
        return GameGet(
            **dict(self._settings),
            status=self.get_status(),
            hasPassword=(not (self._settings.password is None)),
            players=self.get_players_count(),
            id=self._id
        )

    def get_short_game_info(self) -> GameShortGet:
        return GameShortGet(
            **dict(self._settings),
            status=self.get_status(),
            hasPassword=(not (self._settings.password is None)),
            players=self.get_players_count(),
        )

    def receive_action(self, player: PlayerManager, action: Dict[str, Any]):
        print(f"Got {action['type']} from {player.get_name()}")
        self._game.execute_action(player, action)

    def get_host(self) -> User:
        return self._host

    def is_full(self) -> bool:
        return self.get_players_count() >= self._settings.maxPlayers

