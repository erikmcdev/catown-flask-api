from datetime import date

from domain import model
from service.unit_of_work import AbstractUnitOfWork


class NotEnoughRoom(Exception):
    pass


class NoSuchHouse(Exception):
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
        if not house.is_there_room() and uow.repo.get_any_available_house() is None:
            empty_house = model.House.new_home()
            uow.repo.add_house(empty_house)
        uow.repo.add_cat(cat)
        uow.commit()
        result = (cat.id, cat.house.count)
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
