from datetime import date
from domain.model import House, Cat, Nature

def make_cat():
    return Cat.create_cat("Iona", date(2018, 7, 9), Nature(3))

def make_cats(quantity: int = 2): 
    cats = []
    for i in range(quantity):
        if i % 2 != 0:
            cats.append(Cat.create_cat("Iona", date(2018, 7, 9), Nature(2)))
        else:
            cats.append(Cat.create_cat('Lain', date(2019, 4, 23), Nature(4)))
    return cats

def compute_coexistence(house: House):
    cats = list(house._cats)
    coex_count = 0.0
    for i in range(len(cats) - 1):
        coex_count += sum(map(cats[i].coexistence, cats[i+1:]))
    return coex_count

def test_take_in_cat():
    house = House.new_home()
    cat = make_cat()

    house.take_in(cat)

    assert house.has_cat(cat)
    assert house.coexistence == compute_coexistence(house)

def test_take_in_repeated_cat():
    cat = make_cat()
    house = House.new_home(cat)
    result = house.take_in(cat)

    assert result is None and house.has_cat(cat)
    assert house.coexistence == compute_coexistence(house)

def test_take_in_full_house():
    cats = make_cats(4)
    house = House.new_home(*cats)
    cat = make_cat()

    result = house.take_in(cat)
    
    assert result is None and not house.has_cat(cat)
    assert house.coexistence == compute_coexistence(house)
