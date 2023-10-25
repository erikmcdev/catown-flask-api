import uuid
import pytest
import requests
from random import randint

import config

def random_suffix():
    return uuid.uuid4().hex[:6]

def random_name(name=""):
    return f"name-{name}-{random_suffix()}"

def random_nature():
    return randint(1,6)

def random_birthdate():
    return f"20{randint(12, 22)}-{randint(1, 12)}-{randint(1,28)}"

def post_to_add_cat(new_house = False):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_cat", json={"name": random_name(), "birthdate": random_birthdate(), "nature": random_nature(), 
                                "new_house": new_house}
    )
    assert r.status_code == 201
    return r.json()["id"], r.json()["house_id"], r.json()["count"]

@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_transfer_path_returns_201():
    origin_cat_id = post_to_add_cat()[0]
    destiny_house_id = post_to_add_cat(True)[1]

    data = {"cat_id": origin_cat_id, "destiny_id": destiny_house_id}

    url = config.get_api_url()
    r = requests.post(f"{url}/transfer", json=data)

    assert r.status_code == 201
    assert r.json()["house_id"] == destiny_house_id

@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_transfer_path_returns_400_and_error_message():
    count = 0
    result = post_to_add_cat(True)
    origin_cat_id = result[0] 
    origin_house_id = result[1] 
    while count != 4:
        result = post_to_add_cat()
        destiny_house_id = result[1]
        if origin_house_id != destiny_house_id: count = result[2]
    data = {"cat_id": origin_cat_id, "destiny_id": destiny_house_id}
    url = config.get_api_url()
    r = requests.post(f"{url}/transfer", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Not enough room in {destiny_house_id} House"
