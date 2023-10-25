from datetime import date
from service.unit_of_work import AbstractUnitOfWork

from domain import model

class NotEnoughRoom(Exception):
    pass

def add_cat(
        name: str, birthdate: date, nature: str, uow: AbstractUnitOfWork, 
        new_house = False
)-> tuple:
    cat = model.Cat.create_cat(name, birthdate, nature)
    with uow:
        if new_house or (house := uow.repo.get_any_available_house()) is None:
            house = model.House.new_home()
        house.take_in(cat)
        uow.repo.add_cat(cat)
        uow.commit()
        result = (cat.id, cat.house.id, cat.house.count)
    return result

def transfer(
        destination_id: str, cat_id: str, uow: AbstractUnitOfWork
)-> str:
    with uow:
        house = uow.repo.get_house(destination_id)
        if not house.is_there_room():
            raise NotEnoughRoom(f"Not enough room in {house.id} House")
        cat = uow.repo.get_cat(cat_id)
        cat_id = model.transfer(house, cat)
        uow.commit()
    return str(cat_id)

def list_houses(uow: AbstractUnitOfWork)-> list:
    with uow:
        houses = uow.repo.list_houses()
        result = [h.to_dict() for h in houses]
    return result