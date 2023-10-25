from domain import model
from service import unit_of_work
from sqlalchemy import text
from adapters import orm
from datetime import date

def insert_house(session):
    result = session.execute(
        orm.house.insert().values(coexistence=0.0, count=0)
    )
    return result.inserted_primary_key[0]
def insert_cat(session, name, birthdate, nature, house_id):
    result = session.execute(
        orm.cat.insert().values(name=name, birthdate=birthdate, nature=nature, house_id=house_id)
    )
    return result.inserted_primary_key[0]
def get_cat_house_id(session, cat_id):
    house_id = session.query(orm.model.Cat.house_id).filter(orm.model.Cat.id==cat_id).scalar()
    return house_id
def test_uow_can_retrieve_cats_and_transfer(session_factory):
    session =  session_factory()
    house1_id = insert_house(session)
    house2_id = insert_house(session)
    cat_id = insert_cat(session, "Jordan", date(2017,4,17), model.Nature(2), house1_id)

    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        cat = uow.repo.get_cat(cat_id)
        house2 = uow.repo.get_house(house2_id)
        model.transfer(house2, cat)
        uow.commit()
    cats_house_id = get_cat_house_id(session, cat_id)
    assert str(cats_house_id) == house2_id

def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        house_id = insert_house(uow.session)
        insert_cat(uow.session, "Lando", date(2021,4,6), model.Nature.PARTY_GOING, house_id)
    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "house"')))
    assert rows == []
