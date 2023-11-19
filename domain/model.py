from __future__ import annotations
from datetime import date
from enum import Enum
from uuid import UUID, uuid4
from dataclasses import dataclass

@dataclass(frozen=True)
class Nature(Enum):
    LEADER_OF_THE_GANG = 1
    NINJA_INVESTIGATOR = 2
    PARTY_GOING = 3
    LONE_TIGER = 4
    COMFORT_CONNAISSEUR = 5
    BUSY_GOSSIP = 6

    def relation(self, other: Nature, connections = {
        LEADER_OF_THE_GANG: {LEADER_OF_THE_GANG: -.25, NINJA_INVESTIGATOR: .2, PARTY_GOING: .03, LONE_TIGER: -.2},
        NINJA_INVESTIGATOR: {LEADER_OF_THE_GANG: .15, PARTY_GOING: .03 ,LONE_TIGER: .1},
        PARTY_GOING: {PARTY_GOING: .2, LONE_TIGER: -.1, BUSY_GOSSIP: .2},
        LONE_TIGER: {LEADER_OF_THE_GANG: -.5, NINJA_INVESTIGATOR: .05},
        COMFORT_CONNAISSEUR: {LEADER_OF_THE_GANG: -.5, LONE_TIGER: .1},
        BUSY_GOSSIP: {LEADER_OF_THE_GANG: .02, PARTY_GOING: .05, LONE_TIGER: -.05, COMFORT_CONNAISSEUR: -.08, BUSY_GOSSIP: .05}
    }):
        return connections[self.value].get(other.value, 0)

class Cat:
    def __init__(self, id: UUID, name: str, birthdate: date, nature: Nature):
        if isinstance(id, str):
            id = UUID(id)
        self.id = id
        self.name = name
        self.birthdate = birthdate
        self.nature = nature
        self.house = None

    def __repr__(self):
        return f"<Cat {self.id} {self.name}>"

    def __eq__(self, other):
        if not isinstance(other, Cat):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
    
    @staticmethod
    def create_cat(name: str, birthdate: date, nature: str):
        cat = Cat(uuid4(), name, birthdate, nature)
        return cat
    
    def _change_house(self, house: House):
        self.house = house
    
    def coexistence(self, other: Cat):
        return self.nature.relation(other.nature) + other.nature.relation(self.nature)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "birthdate": self.birthdate,
            "nature": self.nature.name.replace('_', ' ').lower()
        }

class House:

    def __init__(self, id: UUID) -> None:
        if isinstance(id, str):
            id = UUID(id)
        self.id = id
        self._cats = set()
        self.coexistence = 0.0
        self.count = 0

    def __repr__(self):
        return f"<House {self.id}>"

    def __eq__(self, other):
        if not isinstance(other, House):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
    
    def get_cats(self):
        return self._cats
    
    def take_in(self, cat: Cat):
        if cat not in self._cats and self.is_there_room():
            self.coexistence += sum(map(cat.coexistence, self._cats))
            self._cats.add(cat)
            self.count += 1
            cat._change_house(self)
            return cat
        return None
    
    def has_cat(self, cat: Cat) -> bool:
        return cat in self._cats
    
    def is_there_room(self) -> bool:
        return self.count < 4
    
    @staticmethod
    def new_home(*cats: list[Cat]):
        new_house = House(uuid4())
        for c in cats:
            new_house.take_in(c)
        return new_house
    
    def to_dict(self):
        return {
            "id": self.id,
            "count": self.count,
            "coex": self.coexistence
        }

def transfer(destination: House, cat: Cat) -> str:
    if destination.is_there_room() and destination != cat.house:
        old_house = cat.house
        old_house.count -= 1
        old_house.coexistence -= sum(map(cat.coexistence, cat.house._cats))
        destination.take_in(cat)
        old_house._cats.discard(cat)
        return str(cat.id)
    return None
