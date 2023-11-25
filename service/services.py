from datetime import date

from domain import model
from service.unit_of_work import AbstractUnitOfWork


class NotEnoughRoom(Exception):
    pass


class NoSuchHouse(Exception):
    pass

class NoNeedForCreatingHouse(Exception):
    pass

def add_cat(
    name: str, birthdate: date, nature: str, house_id: str, uow: AbstractUnitOfWork
) -> tuple:
    cat = model.Cat.create_cat(name, birthdate, nature)
    with uow:
        house = uow.repo.get_house(house_id)
        if not house:
            raise NoSuchHouse(f"No such house with id {house_id}")
        if not house.is_there_room():
            raise NotEnoughRoom(f"Not enough room in house {house.id}")
        house.take_in(cat)
        empty_house = None
        if not house.is_there_room() and uow.repo.get_any_available_house() is None:
            empty_house = model.House.new_home()
            uow.repo.add_house(empty_house)
        uow.repo.add_cat(cat)
        uow.commit()
        result = {"id": cat.id, "count": house.count, "new_home_id": None if empty_house is None else empty_house.id}
    return result


def transfer(destination_id: str, cat_id: str, uow: AbstractUnitOfWork) -> str:
    with uow:
        house = uow.repo.get_house(destination_id)
        if not house:
            raise NoSuchHouse(f"No such house with id {destination_id}")
        if not house.is_there_room():
            raise NotEnoughRoom(f"Not enough room in {house.id} House")
        cat = uow.repo.get_cat(cat_id)
        cat_id = model.transfer(house, cat)
        uow.commit()
    return str(cat_id)

def create_house(uow: AbstractUnitOfWork) -> str:
    with uow:
        house = uow.repo.get_any_available_house()
        if house:
            raise NoNeedForCreatingHouse(f"There's already a valid house with id {house.id}")
        house = model.House.new_home()
        uow.repo.add_house(house)
        uow.commit()
        result = house.id
    return result




def list_houses(uow: AbstractUnitOfWork) -> list:
    with uow:
        houses = uow.repo.list_houses()
        result = [h.to_dict() for h in houses]
    return result


def get_cats_by_house(house_id: str, uow: AbstractUnitOfWork) -> list:
    with uow:
        house = uow.repo.get_house(house_id)
        if not house:
            raise NoSuchHouse(f"No such house {house_id}")
        cats = house.get_cats()
        result = [c.to_dict() for c in cats]
    return result
