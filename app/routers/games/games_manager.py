from fastapi import HTTPException, status
from typing import Dict, List, Optional

import string
import random

from ..users.database import User
from .game_manager import GameManager
from .models import GameStatus, GamePost, GameShortGet

code_length = 5


def generate_code():
    return ''.join(
        [random.choice(string.ascii_uppercase) for _ in range(code_length)])


class GamesManager:
    def __init__(self):
        self.games: Dict[string, GameManager] = {}

    def find_game(self, _id: str) -> Optional[GameManager]:
        if not (_id in self.games):
            return None

        return self.games[_id]

    def get_available_code(self):
        # TODO attempts counter
        while True:
            code = generate_code()

            if self.find_game(code) is None:
                return code

    def create_game(self, host: User, game: GamePost) -> str:
        code = self.get_available_code()

        self.games[code]: GameManager = GameManager(host, game, code)

        return code

    def delete_game(self, user: User, code: str):
        game = self.find_game(code)
        if game is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
            )

        if user.uuid != game.get_host().uuid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not host of this game"
            )

        del self.games[code]

    def get_public_games(self) -> List[GameShortGet]:

        def filter_game(game: GameShortGet) -> bool:
            return (not game.private) and (
                    game.hotJoin or game.status == GameStatus.Lobby)

        return list(filter(filter_game,
                           map(lambda game: game.get_short_game_info(),
                               self.games.values()
                               )
                           ))
