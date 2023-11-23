import abc
from domain import model

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add_house(self, house: model.House):
        raise NotImplementedError

    @abc.abstractmethod
    def get_house(self, id) -> model.House:
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_any_available_house(self) -> model.House:
        raise NotImplementedError
    
    @abc.abstractmethod
    def add_cat(self, cat: model.Cat):
        raise NotImplementedError

    @abc.abstractmethod
    def get_cat(self, id) -> model.Cat:
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_cats_by_house(self, house_id: str):
        raise NotImplementedError
    
    @abc.abstractmethod
    def list_cats(self):
        raise NotImplementedError
    @abc.abstractmethod
    def list_houses(self):
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add_cat(self, cat: model.Cat):
        self.session.add(cat)
    
    def add_house(self, house: model.House):
        self.session.add(house)

    def get_cat(self, cat_id: int):
        return self.session.query(model.Cat).filter_by(id=cat_id).one()
    
    def get_cats_by_house(self, house_id: str):
        return self.session.query(model.Cat).filter_by(house_id=house_id)
    
    def get_house(self, house_id: str):
        return self.session.query(model.House).filter_by(id=house_id).one_or_none()
    
    def get_any_available_house(self) -> model.House:
        return self.session.query(model.House).filter(model.House.count < 4).first()

    def list_cats(self):
        return self.session.query(model.Cat).all()
    
    def list_houses(self):
        return self.session.query(model.House).order_by(model.House.count).all()