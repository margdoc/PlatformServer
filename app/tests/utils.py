from fastapi.testclient import TestClient
import random
import string

from app.routers.users.database import User

common_password = "password"


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def register_user(client: TestClient, username: str, email: str = "xd@xd.xd",
                  password: str = common_password, name: str = "name",
                  lastname: str = "lastname"):
    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "name": name,
            "lastname": lastname,
            "password": password
        }
    )

    assert register_response.status_code == 200

    return register_response.json()


def login_user(client: TestClient, username: str, password: str):
    login_response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    login_responseJSON = login_response.json()

    assert login_responseJSON["tokenType"] == "bearer"

    return login_responseJSON


def get_user(client: TestClient, token: str):
    me_response = client.get(
        "/users/me",
        headers=auth_header(token)
    )

    assert me_response.status_code == 200

    return me_response.json()


def add_random_user(client: TestClient, length: int = 10) -> User:
    user = {
        "username": "".join([random.choice(string.ascii_letters) for _ in range(length)]),
        "email": "".join([random.choice(string.ascii_lowercase) for _ in range(length + 1)])
                 + "@gmail.com",
        "name": "X",
        "lastname": "D",
    }

    return User(**register_user(client, **user))


def create_game(client: TestClient, token: str,
                name: str = "game",
                private: bool = False,
                description: str = "",
                max_players: int = 2,
                hot_join: bool = True
                ):
    response = client.post("/games/",
                           json={
                               "name": name,
                               "private": private,
                               "description": description,
                               "maxPlayers": max_players,
                               "hotJoin": hot_join
                           },
                           headers=auth_header(token)
                           )

    assert response.status_code == 200
    return response.json()
