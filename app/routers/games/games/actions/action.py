from pydantic import BaseModel
from typing import Dict, Any, Type
import json


class Action(BaseModel):
    pass


actions_classes: Dict[str, Type[Action]] = {}


def action_wrapper(cls: Type[Action]):
    actions_classes[cls.__name__] = cls
    return cls


def dict_to_action(object_dict: Dict[str, Any]) -> Action:
    cls = actions_classes[object_dict["type"]]
    return cls(**object_dict)


def action_to_json(action: Action) -> str:
    return json.dumps({
        **json.loads(action.json()),
        "type": action.__class__.__name__
    })
