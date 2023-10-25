import pytest
from datetime import date
from adapters import repository
from service import services, unit_of_work
from domain.model import Nature

class FakeRepository(repository.AbstractRepository):
    def __init__(self, houses = set(), cats = set()):
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
    cat_id, house_id, house_count = services.add_cat("Felix", date(2021, 4, 28), Nature.PARTY_GOING, uow)
    assert uow.repo.get_cat(cat_id) is not None
    assert uow.repo.get_house(house_id) is not None
    assert uow.committed

def test_transfer():
    uow = FakeUnitOfWork()
    cat1_id = services.add_cat("Felix", date(2021, 4, 28), Nature.PARTY_GOING, uow)[0]
    # Next one gonna be add on a new house
    house2_id = services.add_cat("Asura", date(2022, 8, 12), Nature.NINJA_INVESTIGATOR, uow, True)[1]
    result = services.transfer(house2_id, cat1_id, uow)
    assert result == str(cat1_id)
    assert house2_id == uow.repo.get_cat(cat1_id).house.id

def test_transfer_error_not_enough_room():
    uow = FakeUnitOfWork()
    house1_id = services.add_cat("Felix", date(2021, 4, 28), Nature.PARTY_GOING, uow)[1]
    services.add_cat("Asura", date(2022, 8, 12), Nature.NINJA_INVESTIGATOR, uow)
    services.add_cat("Robert", date(2017,11,4), Nature.BUSY_GOSSIP, uow)
    services.add_cat("Lois", date(2021,2,24), Nature.COMFORT_CONNAISSEUR, uow)
    cat5_id = services.add_cat("Forbin", date(2020,6,15), Nature.COMFORT_CONNAISSEUR, uow)[0]

    with pytest.raises(services.NotEnoughRoom, match=f"Not enough room in {house1_id} House"):
        services.transfer(house1_id, cat5_id, uow)

def test_commits():
    uow = FakeUnitOfWork()
    house1_id = services.add_cat("Felix", date(2021, 4, 28), Nature.PARTY_GOING, uow)[1]
    cat2_id = services.add_cat("Asura", date(2022, 8, 12), Nature.NINJA_INVESTIGATOR, uow, True)[0]
    services.transfer(house1_id, cat2_id, uow)
    
    assert uow.committed