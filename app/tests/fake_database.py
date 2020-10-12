import functools
import uuid

from ..routers.users.database import reset_fake_collection, get_collection, UserDB
from ..utils import get_password_hash

admin = {
    "username": "margdoc",
    "password": "pytest",
    "email": "margdoc@python.com",
    "name": "Mikołaj",
    "lastname": "Python",
}


def database_test(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_fake_collection()

        get_collection().insert_one(
            dict(UserDB(
                **admin,
                hashedPassword=get_password_hash(admin["password"]),
                isActive=True,
                isSuperuser=True,
                uuid=uuid.uuid4()
            ))
        )

        return func(*args, **kwargs)

    return wrapper
