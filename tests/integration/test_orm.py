from domain import model
from datetime import date
from adapters import orm
from uuid import UUID

def test_retrieve_cats(session):

    result = session.execute(orm.house.insert().values(coexistence=0.0, count=0))
    house_id = UUID(result.inserted_primary_key[0])
    result = session.execute(orm.cat.insert().values(
        name="Lain", birthdate=date(2019,6,12), nature=model.Nature.BUSY_GOSSIP, house_id=house_id)
    )
    cat1_id = UUID(result.inserted_primary_key[0])
    
    result = session.execute(orm.cat.insert().values(
        name="Felix", birthdate=date(2014,11,28), nature=model.Nature.PARTY_GOING, house_id=house_id)
    )
    cat2_id = UUID(result.inserted_primary_key[0])
    
    expected = [
        model.Cat(cat1_id, "Lain", date(2019,6,12), model.Nature.LONE_TIGER),
        model.Cat(cat2_id, "Felix", date(2014,11,28), model.Nature.PARTY_GOING),
    ]
    assert session.query(model.Cat).all() == expected

def test_save_cats(session):
    house = model.House.new_home()
    session.add(house)
    session.commit()

    cat = model.Cat.create_cat("Lain", date(2019,6,12), model.Nature.LONE_TIGER)
    house.take_in(cat)
    session.add(cat)
    session.commit()

    rows = session.execute(
        orm.cat.select().where(orm.cat.c.id == cat.id)
    )

    assert list(rows) == [(cat.id, "Lain", date(2019,6,12), model.Nature.LONE_TIGER, house.id)]

def test_retrive_houses(session):

    result = session.execute(orm.house.insert().values(coexistence=0.0, count=0))
    house1_id = UUID(result.inserted_primary_key[0])
    result = session.execute(orm.house.insert().values(coexistence=0.0, count=0))
    house2_id = UUID(result.inserted_primary_key[0])
    expected = [
        model.House(house1_id),
        model.House(house2_id),
    ]

    assert session.query(model.House).all() == expected

def test_save_houses(session):
    house = model.House.new_home()
    session.add(house)
    session.commit()

    rows = session.execute(
        orm.house.select().where(orm.house.c.id == house.id)
    )
    assert list(rows) == [(house.id, house.coexistence, house.count)]