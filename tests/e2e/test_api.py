import uuid
from random import randint

import pytest
import requests

import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_name(name=""):
    return f"name-{name}-{random_suffix()}"


def random_nature():
    natures = [
        "LEADER_OF_THE_GANG",
        "NINJA_INVESTIGATOR",
        "PARTY_GOING",
        "LONE_TIGER",
        "COMFORT_CONNAISSEUR",
        "BUSY_GOSSIP",
    ]
    return natures[randint(0, 5)]


def random_birthdate():
    return f"20{randint(12, 22)}-{randint(1, 12)}-{randint(1,28)}"


def post_to_add_cat(house_id: str):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_cat",
        json={
            "name": random_name(),
            "birthdate": random_birthdate(),
            "nature": random_nature(),
            "house_id": house_id,
        },
    )
    assert r.status_code == 201
    return r.json()["id"], r.json()["count"]


def get_valid_house_id():
    url = config.get_api_url()
    r = requests.get(f"{url}/houses")
    assert r.status_code == 200
    return r.json()[0]["id"]


def get_valid_cat_id_for_transfer(exclude_house_id):
    url = config.get_api_url()
    r = requests.get(f"{url}/houses")
    assert r.status_code == 200

    for house in r.json():
        if house["id"] != exclude_house_id and house["count"] > 0:
            house_id = house["id"]
            break
    r = requests.get(f"{url}/cats", {"house_id": house_id})
    assert r.status_code == 200
    return r.json()[0]["id"]


def get_valid_house_id_for_transfer(exclude_house_id):
    url = config.get_api_url()
    r = requests.get(f"{url}/houses")
    assert r.status_code == 200

    for house in r.json():
        if house["id"] != exclude_house_id and house["count"] < 4:
            return house["id"]


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_transfer_path_returns_201():
    house_id = get_valid_house_id()
    origin_cat_id = post_to_add_cat(house_id)[0]
    destiny_house_id = get_valid_house_id_for_transfer(house_id)

    data = {"cat_id": origin_cat_id, "destiny_id": destiny_house_id}

    url = config.get_api_url()
    r = requests.post(f"{url}/transfer", json=data)

    assert r.status_code == 201
    assert r.json()["house_id"] == destiny_house_id


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_transfer_path_returns_400_and_error_message():
    house_id = get_valid_house_id()
    count = post_to_add_cat(house_id)[1]
    while count < 4:
        result = post_to_add_cat(house_id)
        count = result[1]
    origin_cat_id = get_valid_cat_id_for_transfer(house_id)
    data = {"cat_id": origin_cat_id, "destiny_id": house_id}
    url = config.get_api_url()
    r = requests.post(f"{url}/transfer", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Not enough room in {house_id} House"
