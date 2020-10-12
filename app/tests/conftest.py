import pytest

from ..routers.users.database import set_fake_collection, delete_fake_collection


@pytest.fixture(scope="session", autouse=True)
def prepare_db(request):
    set_fake_collection()

    request.addfinalizer(delete_fake_collection)
