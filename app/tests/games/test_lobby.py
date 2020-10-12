from fastapi.websockets import WebSocket
from fastapi.testclient import TestClient

from ... import app
from ...routers.users.database import UserShort
from ..fake_database import database_test
from ..utils import login_user, add_random_user, common_password, auth_header, create_game

client = TestClient(app)


@database_test
def test_joining():
    user = add_random_user(client)

    token = login_user(client, user.username, common_password)["accessToken"]

    code = create_game(client, token)["code"]

    with client.websocket_connect(
            f"/games/{code}/ws",
            headers=auth_header(token)
         ) as websocket:
        websocket: WebSocket

        response = websocket.receive_text()
        assert response == "Joining"

        data = websocket.receive_json()
        print(data)

        """"
        assert data == {
            "type": "LobbyInitAction",
            "host": user.username,
            "messages": [],
            "players": [dict(UserShort(**dict(user)))]
        }
        """
