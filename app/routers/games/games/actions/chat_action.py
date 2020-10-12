from .action import Action, action_wrapper


@action_wrapper
class ChatActionPost(Action):
    chatId: str
    message: str


@action_wrapper
class ChatActionGet(Action):
    chatId: str
    message: str
    author: str
    date: str

