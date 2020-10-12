from fastapi.testclient import TestClient
import random

from ... import app
from ...routers.users.database import UserShort
from ..fake_database import database_test, admin
from ..utils import register_user, login_user, add_random_user, auth_header

client = TestClient(app)


@database_test
def test_all_with_superuser():
    token = login_user(client,
                       admin["username"],
                       admin["password"]
                       )["accessToken"]

    response = client.get(
        "users/all",
        headers=auth_header(token)
    )

    assert response.status_code == 200
    assert response.json() == [dict(UserShort(**admin))]


@database_test
def test_all_without_superuser():
    response = client.get(
        "users/all"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    user = {
        "username": "m",
        "password": "k",
    }

    register_user(client, username=user["username"], password=user["password"])
    token = login_user(client,
                       user["username"],
                       user["password"]
                       )["accessToken"]

    response = client.get(
        "users/all",
        headers=auth_header(token)
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "You are not superuser"


@database_test
def test_all_with_superuser_with_many_users():
    users_count = random.randrange(5, 20)

    users = [dict(UserShort(**admin))]
    for i in range(users_count):
        users.append(dict(UserShort(**dict(add_random_user(client, i + 1)))))

    token = login_user(client,
                       admin["username"],
                       admin["password"]
                       )["accessToken"]

    response = client.get(
        "users/all",
        headers=auth_header(token)
    )

    assert response.status_code == 200
    for user_in_db in response.json():
        assert user_in_db in users


@database_test
def test_get_user_without_superuser():
    response = client.get(
        f"users/{admin['username']}"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    user = {
        "username": "m",
        "password": "k",
    }

    register_user(client, username=user["username"], password=user["password"])
    token = login_user(client,
                       user["username"],
                       user["password"]
                       )["accessToken"]

    response = client.get(
        f"users/{admin['username']}",
        headers=auth_header(token)
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "You are not superuser"
