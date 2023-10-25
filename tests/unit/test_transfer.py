from domain.model import transfer, House
from test_model import make_cats, compute_coexistence

def test_transfer():
    cats = make_cats(3)
    house_origin = House.new_home(*cats)
    house_dest = House.new_home()

    cat = cats[0]
    transfer(house_dest, cat)

    assert not house_origin.has_cat(cat) and house_dest.has_cat(cat)
    assert house_origin.coexistence == compute_coexistence(house_origin)
    assert house_dest.coexistence == compute_coexistence(house_dest)

def test_transfer_to_same_house():
    cats = make_cats(3)
    house_origin = House.new_home(*cats)
    cat = next(iter(house_origin._cats))
    transfer(house_origin, cat)

    assert house_origin.has_cat(cat) and house_origin.count == 3
    assert house_origin.coexistence == compute_coexistence(house_origin)

def test_transfer_to_full_house():
    house_origin = House.new_home(*make_cats())
    house_dest = House.new_home(*make_cats(4))
    cat = next(iter(house_origin._cats))
    transfer(house_dest, cat)

    assert house_origin.has_cat(cat) and not house_dest.has_cat(cat)
    assert house_origin.coexistence == compute_coexistence(house_origin)
    assert house_dest.coexistence == compute_coexistence(house_dest)