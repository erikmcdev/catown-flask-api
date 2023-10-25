from domain import model
from adapters import repository
from datetime import date
from sqlalchemy import select
from adapters import orm

def test_repository_can_save_a_cat(session):
    house = model.House.new_home()
    cat = model.Cat.create_cat('Robert', date(2017,11,4), model.Nature.BUSY_GOSSIP)
    house.take_in(cat)
    
    repo = repository.SqlAlchemyRepository(session)
    repo.add_cat(cat)
    session.commit()
    
    rows = session.execute(
        orm.cat.select().where(orm.cat.c.id==cat.id)
    )
    assert list(rows) == [(cat.id, 'Robert', date(2017,11,4), model.Nature.BUSY_GOSSIP, cat.house.id)]

def test_repository_can_retrieve_a_cat(session):
    house = insert_house(session)
    expected = insert_cat(session, house)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get_cat(expected.id)

    assert expected == retrieved
    assert house == retrieved.house

def insert_cat(session, house: model.House) -> model.Cat:
    result = session.execute(
        orm.cat.insert(), {"name": "Robert", "birthdate": date(2017,11,4),
                           "nature": model.Nature.BUSY_GOSSIP, "house_id": house.id}
    )

    cat_id = result.inserted_primary_key[0]
    cat = model.Cat(cat_id, "Robert",date(2017,11,4), model.Nature.BUSY_GOSSIP)
    return cat 

def insert_house(session):
    result = session.execute(
        orm.house.insert(), {"coexistence": 0.0, "count": 0}
    )
    house = model.House(result.inserted_primary_key[0])
    
    return house

def test_repository_can_save_a_house_with_cats(session):
    
    cat1 = model.Cat.create_cat("Robert", date(2017,11,4), model.Nature.BUSY_GOSSIP)
    cat2 = model.Cat.create_cat("Lois", date(2021,2,24),model.Nature.COMFORT_CONNAISSEUR)
    cat3 = model.Cat.create_cat("Forbin", date(2020,6,15), model.Nature.LEADER_OF_THE_GANG)
    
    house = model.House.new_home(cat1, cat2, cat3)

    repo = repository.SqlAlchemyRepository(session)
    repo.add_house(house)
    session.commit()

    rows = session.execute(
        orm.house.select().where(orm.house.c.id == house.id)
    )

    cat_rows = session.execute(
        select(orm.cat.c.id).where(orm.cat.c.house_id == house.id)
    )

    assert list(rows) == [(house.id, house.coexistence, house.count)]
    assert set(cat_rows) == {(cat1.id,), (cat2.id,), (cat3.id,)}

def test_repository_can_retrieve_a_house_with_cats(session):
    expected = insert_house(session)
    cat1 = insert_cat(session, expected)
    cat2 = insert_cat(session, expected)
    cat3 = insert_cat(session, expected)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get_house(expected.id)

    assert retrieved == expected  # House.__eq__ only compares id
    assert retrieved.has_cat(cat1)
    assert retrieved.has_cat(cat2)
    assert retrieved.has_cat(cat3)