from __future__ import annotations

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


def create_house():
    url = config.get_api_url()
    r = requests.post(f"{url}/create_house")
    assert r.status_code == 201
    house_id = r.json()["house_id"]
    return house_id


def set_initial_state():
    url = config.get_api_url()
    house_id = create_house()
    count = post_to_add_cat(house_id)["count"]
    while count < 4:
        count = post_to_add_cat(house_id)["count"]
    r = requests.get(f"{url}/houses")
    assert r.status_code == 200
    return r


def post_to_add_cat(house_id: str) -> tuple(str, int):
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
    response = r.json()
    print(response)
    return {
        "id": response["id"],
        "count": response["count"],
        "new_home_id": response.get("new_home_id"),
    }


def get_valid_house_id(exclude=None):
    url = config.get_api_url()
    r = requests.get(f"{url}/houses")
    assert r.status_code == 200

    house = next((h for h in r.json() if h["id"] != exclude), None)
    return house["id"]


def get_valid_cat_id_for_transfer(exclude=None):
    url = config.get_api_url()
    r = requests.get(f"{url}/houses")
    assert r.status_code == 200

    house = next((h for h in r.json() if h["id"] != exclude and h["count"] > 0), None)
    r = requests.get(f"{url}/cats", {"house_id": house["id"]})
    assert r.status_code == 200
    return r.json()[0]["id"], house["id"], house["count"]


def get_valid_house_id_for_transfer(exclude=None):
    url = config.get_api_url()
    r = requests.get(f"{url}/houses")
    assert r.status_code == 200
    if len(r.json()) == 0:
        r = set_initial_state()
    house = next((h for h in r.json() if h["id"] != exclude and h["count"] < 4), None)

    return house["id"]


def get_full_house():
    url = config.get_api_url()
    r = requests.get(f"{url}/houses")
    assert r.status_code == 200
    houses = r.json()
    print("HOLAAAAA", houses)
    house_id = houses[-1]["id"] if len(houses) > 0 else create_house()
    count = houses[-1]["count"] if len(houses) > 0 else 0
    while count < 4:
        post_res = post_to_add_cat(house_id)
        count = post_res["count"]
    if len(houses) < 2:
        new_home_id = post_res["new_home_id"]
        origin_cat_id = post_to_add_cat(new_home_id)["id"]
    else:
        origin_house_id = houses[0]["id"]
        origin_cat_id = post_to_add_cat(origin_house_id)["id"]
    return {"destiny_id": house_id, "cat_id": origin_cat_id}


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_transfer_path_returns_201():
    destiny_house_id = get_valid_house_id_for_transfer()
    origin_cat_id = get_valid_cat_id_for_transfer(destiny_house_id)[0]

    data = {"cat_id": origin_cat_id, "destiny_id": destiny_house_id}

    url = config.get_api_url()
    r = requests.post(f"{url}/transfer", json=data)

    assert r.status_code == 201
    assert r.json()["house_id"] == destiny_house_id


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_transfer_path_returns_400_and_error_message():
    data_request = get_full_house()
    url = config.get_api_url()
    r = requests.post(f"{url}/transfer", json=data_request)
    assert r.status_code == 400
    assert (
        r.json()["message"] == f"Not enough room in {data_request['destiny_id']} House"
    )
