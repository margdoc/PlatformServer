import pytest
from fastapi.testclient import TestClient

from ... import app
from ..fake_database import database_test
from ..utils import register_user, login_user, get_user, auth_header

client = TestClient(app)


@database_test
def test_basic_funcionalitty():
    email = "test@test.com"
    username = "test"
    name = "Test"
    lastname = "Testowy"
    password = "XD"

    register_user(client, username, email, password, name, lastname)

    login_responseJSON = login_user(client, username, password)

    user = get_user(client, login_responseJSON['accessToken'])
    del user["uuid"]
    assert user == {
        "email": email,
        "username": username,
        "name": name,
        "lastname": lastname,
        "isActive": True,
        "isSuperuser": False
    }


@database_test
def test_register_endpoint():
    requests = [
        ("xd", "xd", 400, "Email is not correct"),
        ("xd", "xd@xd.xd", 200, ""),
        ("xd", "xd@xd.com", 409, "Username is already taken"),
        ("xdxd", "xd@xd.xd", 409, "Email is already taken")
    ]

    for (username, email, status_code, detail) in requests:
        _response = client.post(
            "/auth/register",
            json={
                "email": email,
                "username": username,
                "name": "name",
                "lastname": "lastname",
                "password": "password"
            }
        )

        assert _response.status_code == status_code

        if _response.status_code != 200:
            assert _response.json()["detail"] == detail


@database_test
def test_login_endpoint():
    username = "example"
    password = "test"

    register_user(client, username, password=password)

    get_user(client, login_user(client, username, password)["accessToken"])

    requests = [
        ("exampl", password),
        (username, "pass"),
        ("exa", "testtest")
    ]

    for (_username, _password) in requests:
        _response = client.post(
            "/auth/login",
            data={
                "username": _username,
                "password": _password
            }
        )

        assert _response.status_code == 401
        assert _response.json()["detail"] == "Incorrect username or password"


@database_test
def test_me_without_header_endpoint():
    _response = client.get(
        "/users/me"
    )

    assert _response.status_code == 401
    assert _response.json()["detail"] == "Not authenticated"


# TODO write test for expired jwt token
@database_test
@pytest.mark.parametrize(
    "token", [
        ("xd"),
        (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXJnZG9jIiwiZXhwIjoxNjAxNjQ2NDgzfQ.gvjBdR0v78OcZ0_BrsgJZQwI7xIwOSHsqKvtn3QciRk")
    ]
)
def test_me_with_header_endpoint(token):
    _response = client.get(
        "/users/me",
        headers=auth_header(token)
    )

    assert _response.status_code == 401
    assert _response.json()["detail"] == "Could not validate credentials"
