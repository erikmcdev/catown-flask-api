from sqlalchemy import Table, Column, Integer, String,Float, Date, ForeignKey
from sqlalchemy.orm import relationship, registry
from sqlalchemy.types import TypeDecorator, CHAR, VARCHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

from domain import model


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int
    
    def _uuid_value(self, value):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value         

    def process_result_value(self, value, dialect):
        return self._uuid_value(value)

    def sort_key_function(self, value):
        return self._uuid_value(value)

class Nature(TypeDecorator):
    
    impl = VARCHAR
    cache_ok = True

    def process_bind_param(self, nature: model.Nature, dialect) -> str:
        if nature is not None:
            return nature.name

    def process_result_value(self, value: str, dialect) -> model.Nature:
        if value is not None:
            return model.Nature[value]
        
mapper_registry = registry()

house = Table(
    "house",
    mapper_registry.metadata,
    Column("id", GUID(), primary_key=True, default= lambda: str(uuid.uuid4())),
    Column("coexistence", Float),
    Column("count", Integer)
)

cat = Table(
    "cat",
    mapper_registry.metadata,
    Column("id", GUID(), primary_key=True, default= lambda: str(uuid.uuid4())),
    Column("name", String(20), nullable=False),
    Column("birthdate", Date, nullable=False),
    Column("nature", Nature, nullable=False),
    Column("house_id",GUID(), ForeignKey("house.id"), nullable=False)
)

def start_mappers():
    mapper_registry.map_imperatively(model.House, house, properties = {
        "_cats": relationship(
            model.Cat, backref="house", collection_class=set
        )
    })
    mapper_registry.map_imperatively(model.Cat, cat)
    
    