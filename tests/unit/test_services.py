from datetime import date

import pytest

from adapters import repository
from domain import model
from service import services, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, houses=set(), cats=set()):
        self._houses = set(houses)
        self._cats = set(cats)

    def add_house(self, house):
        self._houses.add(house)
        for c in house._cats:
            self._cats.add(c)

    def get_house(self, id):
        return next((h for h in self._houses if h.id == id), None)

    def get_any_available_house(self):
        return next((h for h in self._houses if h.count < 4), None)

    def add_cat(self, cat):
        self._cats.add(cat)
        self.add_house(cat.house)

    def get_cat(self, id):
        return next((c for c in self._cats if c.id == id), None)

    def get_cats_by_house(self, house_id: str):
        return [c for c in self._cats if c.house_id == house_id]

    def list_cats(self):
        return list(self._cats)

    def list_houses(self):
        return list(self._houses)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.repo = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_cat():
    uow = FakeUnitOfWork()
    house = model.House.new_home()
    uow.repo.add_house(house)

    cat_id = services.add_cat(
        "Felix", date(2021, 4, 28), model.Nature.PARTY_GOING, house.id, uow
    )["id"]
    assert uow.repo.get_cat(cat_id) is not None
    assert uow.repo.get_house(house.id) is not None
    assert uow.committed


def test_transfer():
    uow = FakeUnitOfWork()
    house = model.House.new_home()
    house2 = model.House.new_home()
    uow.repo.add_house(house)
    uow.repo.add_house(house2)

    cat1_id = services.add_cat(
        "Felix", date(2021, 4, 28), model.Nature.PARTY_GOING, house.id, uow
    )["id"]
    cat2_id = services.add_cat(
        "Asura", date(2022, 8, 12), model.Nature.NINJA_INVESTIGATOR, house2.id, uow
    )["id"]

    result = services.transfer(house2.id, cat1_id, uow)
    assert result == str(cat1_id)
    assert house2.id == uow.repo.get_cat(cat1_id).house.id


def test_transfer_error_not_enough_room():
    uow = FakeUnitOfWork()
    house = model.House.new_home()
    house2 = model.House.new_home()
    uow.repo.add_house(house)
    uow.repo.add_house(house2)
    services.add_cat(
        "Felix", date(2021, 4, 28), model.Nature.PARTY_GOING, house.id, uow
    )
    services.add_cat(
        "Asura", date(2022, 8, 12), model.Nature.NINJA_INVESTIGATOR, house.id, uow
    )
    services.add_cat(
        "Robert", date(2017, 11, 4), model.Nature.BUSY_GOSSIP, house.id, uow
    )
    services.add_cat(
        "Lois", date(2021, 2, 24), model.Nature.COMFORT_CONNAISSEUR, house.id, uow
    )
    cat5_id = services.add_cat(
        "Forbin", date(2020, 6, 15), model.Nature.COMFORT_CONNAISSEUR, house2.id, uow
    )["id"]

    with pytest.raises(
        services.NotEnoughRoom, match=f"Not enough room in {house.id} House"
    ):
        services.transfer(house.id, cat5_id, uow)


def test_commits():
    uow = FakeUnitOfWork()
    house = model.House.new_home()
    uow.repo.add_house(house)
    services.add_cat(
        "Asura", date(2022, 8, 12), model.Nature.NINJA_INVESTIGATOR, house.id, uow
    )

    assert uow.committed
