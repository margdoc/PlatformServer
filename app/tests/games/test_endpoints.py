from fastapi.testclient import TestClient

from ... import app
from ..fake_database import database_test, admin
from ..utils import login_user, add_random_user, common_password, auth_header, create_game

client = TestClient(app)


@database_test
def test_create_game():
    user = add_random_user(client)

    token = login_user(client, user.username, common_password)["accessToken"]

    create_game(client, token)


@database_test
def test_public_games():
    user = add_random_user(client)

    token = login_user(client, user.username, common_password)["accessToken"]

    games = [
        {"private": True, "name": "1"},
        {"private": False, "name": "2"},
        {"private": True, "name": "3"},
        {"private": False, "name": "4"},
    ]

    for game in games:
        create_game(client, token, **game)

    response = client.get(
        "/games/",
        headers=auth_header(token)
    )

    assert response.status_code == 200

    response_games = response.json()

    for game in games:
        found = False
        for r_game in response_games:
            if r_game["name"] == game["name"]:
                found = True

        assert (found != game["private"])


@database_test
def test_created_game_status():
    user = add_random_user(client)

    token = login_user(client, user.username, common_password)["accessToken"]

    code = create_game(client, token)["code"]

    response = client.get(
        f"/games/{code}/status",
        headers=auth_header(token)
    )

    assert response.status_code == 200
    assert response.json() == {"status": "Lobby"}


@database_test
def test_delete_game():
    user = add_random_user(client)

    token = login_user(client, user.username, common_password)["accessToken"]

    code = create_game(client, token)["code"]

    response = client.delete(
        f"/games/{code}",
        headers=auth_header(token)
    )

    assert response.status_code == 200

    response = client.get(
        f"/games/{code}/status",
        headers=auth_header(token)
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
