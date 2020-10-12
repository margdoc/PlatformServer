from typing import List, Dict
from uuid import UUID

from ....utils import now_timestamp

from app.routers.users.database import UserShort
from ..player_manager import PlayerManager
from .game import Game, GameEvents
from .actions import Action, ChatActionGet, ChatActionPost, LobbyInitAction


class Lobby(Game):
    def __init__(self, host, send_action):
        super().__init__(host, send_action, {
            GameEvents.OnJoin: self.on_player_join,
            GameEvents.OnReconnect: self.send_init_action
        })
        self._messages_history: List[ChatActionGet] = []
        self._players: Dict[UUID, PlayerManager] = {}

    def on_player_join(self, player: PlayerManager):
        self._players[player.get_uuid()] = player
        self.send_init_action(player)

    def send_init_action(self, player: PlayerManager):
        players_list = list(self._players.values())
        users_list = list(map(
            lambda _player: UserShort(**dict(_player.get_user())),
            players_list
        ))

        player.send_action(
            LobbyInitAction(
                messages=self._messages_history,
                players=users_list,
                host=self.get_host().username
            )
        )

    def reducer(self, player: PlayerManager, action: Action):
        if isinstance(action, ChatActionPost):
            chat_action = ChatActionGet(
                **action,
                author=player.get_name(),
                date=now_timestamp(),
            )
            self._messages_history.append(chat_action)
            self._send_action(chat_action)
