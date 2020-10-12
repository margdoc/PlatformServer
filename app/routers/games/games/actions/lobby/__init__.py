from typing import List

from app.routers.users.database import UserShort
from ..action import Action, action_wrapper
from ..chat_action import ChatActionGet


@action_wrapper
class LobbyInitAction(Action):
    players: List[UserShort]
    messages: List[ChatActionGet]
    host: str
